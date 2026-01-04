<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" encoding="UTF-8"/>

  <xsl:template match="/">
    <html>
      <head>
        <title><xsl:value-of select="rss/channel/title"/></title>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }

          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
            background: #0a0a0f;
            color: #e8e8f0;
            line-height: 1.6;
            min-height: 100vh;
          }

          .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
          }

          header {
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 1px solid #2a2a3a;
          }

          h1 {
            font-size: 1.75rem;
            font-weight: 600;
            color: #00d9ff;
            margin-bottom: 0.5rem;
          }

          .description {
            color: #8888a0;
            font-size: 0.95rem;
          }

          .rss-info {
            margin-top: 1rem;
            padding: 0.75rem 1rem;
            background: #12121a;
            border-radius: 8px;
            border: 1px solid #2a2a3a;
            font-size: 0.85rem;
            color: #6b6b80;
          }

          .rss-info code {
            background: #1a1a2e;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'SF Mono', Consolas, monospace;
            color: #00ff88;
          }

          .item {
            padding: 1.5rem 0;
            border-bottom: 1px solid #1a1a2a;
          }

          .item:last-child {
            border-bottom: none;
          }

          .item-header {
            margin-bottom: 0.75rem;
          }

          .item h2 {
            font-size: 1.1rem;
            font-weight: 500;
            margin: 0;
          }

          .item h2 a {
            color: #818cf8;
            text-decoration: none;
            transition: color 0.2s;
          }

          .item h2 a:hover {
            color: #a5b4fc;
          }

          .date {
            color: #6b6b80;
            font-size: 0.85rem;
            margin-top: 0.25rem;
          }

          .enclosure {
            margin: 1rem 0;
          }

          .enclosure img {
            max-width: 100%;
            border-radius: 8px;
            border: 1px solid #2a2a3a;
          }

          .description-content {
            margin-top: 0.75rem;
            color: #b8b8c8;
            font-size: 0.95rem;
          }

          .description-content p {
            margin: 0.5rem 0;
          }

          .description-content strong {
            color: #e8e8f0;
          }

          .description-content ul {
            margin: 0.5rem 0 0.5rem 1.5rem;
          }

          .description-content li {
            margin: 0.25rem 0;
          }

          .description-content em {
            color: #00d9ff;
            font-style: normal;
          }

          footer {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #2a2a3a;
            text-align: center;
            color: #6b6b80;
            font-size: 0.85rem;
          }

          footer a {
            color: #00ff88;
            text-decoration: none;
          }

          footer a:hover {
            text-decoration: underline;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <header>
            <h1><xsl:value-of select="rss/channel/title"/></h1>
            <p class="description"><xsl:value-of select="rss/channel/description"/></p>
            <div class="rss-info">
              This is an RSS feed. Subscribe by copying the URL into your feed reader.
              <br/>Feed URL: <code><xsl:value-of select="rss/channel/link"/></code>
            </div>
          </header>

          <main>
            <xsl:for-each select="rss/channel/item">
              <article class="item">
                <div class="item-header">
                  <h2><a href="{link}"><xsl:value-of select="title"/></a></h2>
                  <div class="date"><xsl:value-of select="pubDate"/></div>
                </div>
                <xsl:if test="enclosure[@type='image/png' or @type='image/jpeg']">
                  <div class="enclosure">
                    <img src="{enclosure/@url}" alt=""/>
                  </div>
                </xsl:if>
                <div class="description-content">
                  <xsl:value-of select="description" disable-output-escaping="yes"/>
                </div>
              </article>
            </xsl:for-each>
          </main>

          <footer>
            <a href="https://elizaos.github.io/knowledge">elizaOS Knowledge</a>
          </footer>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
