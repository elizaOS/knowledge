import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import re
import numpy as np
import sqlite3
from community import community_louvain

def extract_mentions(text):
    """Extract @ mentions from tweet text."""
    if not isinstance(text, str):
        return []
    return re.findall(r'@(\w+)', text)

def create_interaction_graph(tweets_df, classification_df):
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes (users) with their classification
    classifications = classification_df.set_index('account_name')['classification'].to_dict()
    
    # Create interaction edges
    interactions = defaultdict(int)
    for _, row in tweets_df.iterrows():
        if not isinstance(row['tweet_text'], str):
            continue
            
        source = row['account_name']
        # Add mentions as interactions
        mentions = extract_mentions(row['tweet_text'])
        for target in mentions:
            interactions[(source, target)] += 1
    
    # Add edges to graph with weights
    for (source, target), weight in interactions.items():
        G.add_edge(source, target, weight=weight)
        
        # Add classification data to nodes
        G.nodes[source]['classification'] = classifications.get(source, 'Unknown')
        G.nodes[target]['classification'] = classifications.get(target, 'Unknown')

    return G

def visualize_network(G, min_edge_weight=1):
    # Remove weak connections
    G_filtered = G.copy()
    edges_to_remove = [(u, v) for u, v, d in G_filtered.edges(data=True) if d['weight'] < min_edge_weight]
    G_filtered.remove_edges_from(edges_to_remove)

    # Detect communities
    communities = community_louvain.best_partition(G_filtered.to_undirected())
    
    # Set up the plot
    plt.figure(figsize=(20, 20))
    
    # Calculate node sizes based on degree centrality
    centrality = nx.degree_centrality(G_filtered)
    node_sizes = [v * 5000 for v in centrality.values()]
    
    # Calculate edge widths based on weight
    edge_weights = [G_filtered[u][v]['weight'] for u, v in G_filtered.edges()]
    
    # Set node colors based on classification
    color_map = {
        'Human': 'lightblue',
        'AI': 'red',
        'AI/Uncertain': 'orange',
        'Uncertain': 'yellow',
        'Unknown': 'gray'
    }
    
    node_colors = [color_map[G_filtered.nodes[node].get('classification', 'Unknown')] for node in G_filtered.nodes()]
    
    # Use spring layout with adjusted parameters
    pos = nx.spring_layout(G_filtered, k=1/np.sqrt(len(G_filtered.nodes())), iterations=50)
    
    # Draw the network
    nx.draw(G_filtered, pos,
            node_color=node_colors,
            node_size=node_sizes,
            edge_color='gray',
            width=[w/max(edge_weights)*2 for w in edge_weights],
            alpha=0.7,
            with_labels=True,
            font_size=8)
    
    # Add legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', 
                                 markerfacecolor=color, label=classification,
                                 markersize=10)
                      for classification, color in color_map.items()]
    plt.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1, 1))
    
    # Add title and save
    plt.title('User Interaction Network\nNode size = centrality, Edge width = interaction strength')
    plt.tight_layout()
    plt.savefig('user_interaction_network.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Print network statistics
    print("\nNetwork Statistics:")
    print(f"Number of users: {G_filtered.number_of_nodes()}")
    print(f"Number of interactions: {G_filtered.number_of_edges()}")
    print("\nMost Central Users (by degree centrality):")
    central_users = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
    for user, score in central_users:
        print(f"{user}: {score:.3f}")
    
    # Analyze communities
    print("\nCommunity Analysis:")
    community_sizes = defaultdict(int)
    for node, community_id in communities.items():
        community_sizes[community_id] += 1
    
    print(f"Number of communities detected: {len(community_sizes)}")
    print("\nLargest communities:")
    for community_id, size in sorted(community_sizes.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"Community {community_id}: {size} members")
        members = [node for node, c_id in communities.items() if c_id == community_id]
        print(f"Sample members: {', '.join(members[:5])}\n")

def main():
    # Connect to SQLite database
    conn = sqlite3.connect('db.sqlite')
    
    # Load user messages from logs table
    logs_df = pd.read_sql("""
        SELECT l.userId, a.username as account_name, l.body as tweet_text 
        FROM logs l
        JOIN accounts a ON l.userId = a.id
        WHERE l.body IS NOT NULL
    """, conn)
    print(f"Loaded {len(logs_df)} messages from database")
    
    # Create dummy classification dataframe based on accounts
    accounts_df = pd.read_sql("SELECT id, username as account_name FROM accounts", conn)
    accounts_df['classification'] = 'Human'  # Default classification for all accounts
    
    # Create and analyze the network
    G = create_interaction_graph(logs_df, accounts_df)
    
    # Visualize with different minimum edge weights
    min_weight = 1  # Start with a minimum weight of 1
    print(f"\nGenerating network visualization with minimum edge weight: {min_weight}")
    visualize_network(G, min_edge_weight=min_weight)
    plt.savefig('interaction_network.png', dpi=300, bbox_inches='tight')
    print("Saved network visualization to interaction_network.png")
    plt.close()
    
    conn.close()

if __name__ == "__main__":
    main()
