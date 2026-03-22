// Component for displaying source links in a horizontal scrollable row
import React from 'react';

/**
 * SourceCard - Renders a horizontal scrollable row of source cards
 * 
 * Each card displays a favicon, title (truncated), and domain name.
 * Cards link directly to the source URL.
 * 
 * @param {Object} props
 * @param {Array} props.sources - Array of source objects with title, url
 */
function SourceCard({ sources }) {
  /**
   * Extract domain from URL for display and favicon
   * @param {string} url - Full URL
   * @returns {string} - Domain name
   */
  const getDomain = (url) => {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname.replace('www.', '');
    } catch {
      return url;
    }
  };

  /**
   * Truncate title to specified character limit
   * @param {string} title - Original title
   * @param {number} maxLength - Maximum characters
   * @returns {string} - Truncated title with ellipsis if needed
   */
  const truncateTitle = (title, maxLength = 40) => {
    if (title.length <= maxLength) return title;
    return title.substring(0, maxLength) + '...';
  };

  return (
    <div className="mt-4">
      <p className="text-xs text-gray-500 mb-2 uppercase tracking-wider">Sources</p>
      <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-transparent">
        {sources.map((source, index) => {
          const domain = getDomain(source.url);
          const faviconUrl = `https://www.google.com/s2/favicons?domain=${domain}&sz=16`;
          
          return (
            <a
              key={index}
              href={source.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 bg-gray-800 hover:bg-gray-700 rounded-full px-3 py-1.5 transition-colors duration-200 flex-shrink-0"
            >
              <img
                src={faviconUrl}
                alt=""
                className="w-4 h-4 rounded-sm"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
              <span className="text-xs text-gray-300 truncate max-w-[150px]">
                {truncateTitle(source.title, 35)}
              </span>
              <span className="text-xs text-gray-500">
                {domain}
              </span>
            </a>
          );
        })}
      </div>
    </div>
  );
}

export default SourceCard;
