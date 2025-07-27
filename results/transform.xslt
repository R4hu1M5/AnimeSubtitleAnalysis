<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="html" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">

    <html>
      <head>
        <title>
          <xsl:text>Search Results: </xsl:text>
          <xsl:value-of select="/results/@key"/>
        </title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 2em;
            line-height: 1.6;
          }
          h2 {
            margin-top: 2em;
            border-bottom: 1px solid #ccc;
            padding-bottom: 0.2em;
          }
          .subtitle {
            margin-bottom: 1.5em;
          }
          .lang-label {
            font-weight: bold;
          }
          .jp {
            background-color: #f0f8ff;
            padding: 0.5em;
            border-left: 4px solid #1e90ff;
            margin-top: 0.3em;
          }
          .en {
            background-color: #fef9e7;
            padding: 0.5em;
            border-left: 4px solid #f39c12;
            margin-bottom: 0.8em;
          }
        </style>
      </head>

      <body>
        <h1>
          <xsl:text>Search Results For </xsl:text>
          <xsl:value-of select="/results/@key"/>
        </h1>

        <xsl:for-each select="/results/episode">
          <h2>
            <xsl:value-of select="@title"/>
          </h2>

          <xsl:for-each select="subtitle">
            <div class="subtitle">
              <div class="jp">
                <span class="lang-label">JP:</span>
                <xsl:text> </xsl:text>
                <xsl:value-of select="dialogue[@lang='jp']"/>
              </div>
              <div class="en">
                <span class="lang-label">EN:</span>
                <xsl:text> </xsl:text>
                <xsl:value-of select="dialogue[@lang='en']"/>
              </div>
            </div>
          </xsl:for-each>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
