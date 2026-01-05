<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom"
  exclude-result-prefixes="atom">
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
            border-bottom: 2px solid #FF6B35;
            position: relative;
          }

          .rss-icon {
            position: absolute;
            top: 0;
            right: 0;
            width: 32px;
            height: 32px;
            fill: #FF6B35;
            opacity: 0.8;
            transition: opacity 0.2s;
          }

          .rss-icon:hover {
            opacity: 1;
          }

          h1 {
            font-size: 1.75rem;
            font-weight: 600;
            color: #FF6B35;
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

          .copy-url {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: #1a1a2e;
            padding: 0.4rem 0.75rem;
            border-radius: 6px;
            border: 1px solid #2a2a3a;
            cursor: pointer;
            transition: all 0.2s;
            margin-top: 0.5rem;
          }

          .copy-url:hover {
            border-color: #00CED1;
            background: #1f1f2e;
          }

          .copy-url code {
            background: none;
            padding: 0;
            font-family: 'SF Mono', Consolas, monospace;
            color: #00CED1;
          }

          .copy-url .copy-icon {
            width: 14px;
            height: 14px;
            fill: #6b6b80;
            flex-shrink: 0;
          }

          .copy-url:hover .copy-icon {
            fill: #00CED1;
          }

          .copy-url.copied {
            border-color: #00CED1;
          }

          .copy-url.copied .copy-icon {
            fill: #00CED1;
          }

          .item {
            padding: 1.5rem 0;
            border-bottom: 1px solid #1a1a2a;
          }

          .item:last-child {
            border-bottom: none;
          }

          .item h2 {
            font-size: 1.1rem;
            font-weight: 500;
            margin: 0;
          }

          .item h2 a {
            color: #00CED1;
            text-decoration: none;
            transition: color 0.2s;
          }

          .item h2 a:hover {
            color: #40E0D0;
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

          footer {
            margin-top: 2rem;
            padding-top: 1.5rem;
            border-top: 1px solid #2a2a3a;
            text-align: center;
            color: #6b6b80;
            font-size: 0.85rem;
          }

          footer a {
            color: #00CED1;
            text-decoration: none;
          }

          footer a:hover {
            text-decoration: underline;
          }

          .social-link {
            margin-left: 1rem;
            color: #FF6B35;
          }
        </style>
      </head>
      <body>
        <div class="container">
          <header>
            <a href="{rss/channel/atom:link/@href}" title="Subscribe to this RSS feed">
              <svg class="rss-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <circle cx="6.5" cy="17.5" r="2.5"/>
                <path d="M4 4v3c8 0 14.5 6.5 14.5 14.5h3C21.5 12 12 4 4 4z"/>
                <path d="M4 10v3c5 0 8.5 3.5 8.5 8.5h3C15.5 15 11 10 4 10z"/>
              </svg>
            </a>
            <h1><xsl:value-of select="rss/channel/title"/></h1>
            <p class="description"><xsl:value-of select="rss/channel/description"/></p>
            <div class="rss-info">
              Subscribe to GitHub activity updates from elizaOS.
              <div class="copy-url" onclick="copyFeedUrl(this)" data-url="{rss/channel/atom:link/@href}">
                <svg class="copy-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                </svg>
                <code><xsl:value-of select="rss/channel/atom:link/@href"/></code>
              </div>
            </div>
            <script>
              function copyFeedUrl(el) {
                var url = el.getAttribute('data-url');
                var icon = el.querySelector('.copy-icon');
                var origPath = icon.innerHTML;
                navigator.clipboard.writeText(url).then(function() {
                  el.classList.add('copied');
                  icon.innerHTML = '<path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>';
                  setTimeout(function() {
                    el.classList.remove('copied');
                    icon.innerHTML = origPath;
                  }, 1500);
                });
              }
            </script>
          </header>

          <main>
            <xsl:for-each select="rss/channel/item">
              <article class="item">
                <h2><a href="{link}"><xsl:value-of select="title"/></a></h2>
                <div class="description-content">
                  <xsl:value-of select="description" disable-output-escaping="yes"/>
                </div>
              </article>
            </xsl:for-each>
          </main>

          <footer>
            <a href="https://elizaos.github.io/knowledge">elizaOS Knowledge</a>
            <xsl:if test="rss/channel/atom:link[@rel='related']">
              <a class="social-link" href="{rss/channel/atom:link[@rel='related']/@href}">
                <xsl:value-of select="rss/channel/atom:link[@rel='related']/@title"/>
              </a>
            </xsl:if>
            <div style="margin-top: 0.75rem; font-size: 0.8rem;">
              <span style="color: #6b6b80;">More feeds:</span>
              <a href="feed.xml" style="margin-left: 0.5rem; color: #00ff88;">Intelligence</a>
              <a href="council.xml" style="margin-left: 0.5rem; color: #00ff88;">Council</a>
              <a href="https://elizaos.github.io/rss.xml" style="margin-left: 0.5rem; color: #00ff88;">elizaOS Dev</a>
            </div>
          </footer>
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
