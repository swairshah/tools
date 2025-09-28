import React, { useState } from 'react';
import './index.css';

const App = () => {
  const [activeMenu, setActiveMenu] = useState('home');
  const [activeSidebar, setActiveSidebar] = useState('overview');
  const [dropdownValue, setDropdownValue] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [statusType, setStatusType] = useState('');
  const [isDarkMode, setIsDarkMode] = useState(false);

  const handleButtonClick = () => {
    setStatusMessage('Action completed successfully');
    setStatusType('ok');
    setTimeout(() => {
      setStatusMessage('');
      setStatusType('');
    }, 3000);
  };

  const menuItems = ['home', 'components', 'layouts', 'about'];
  const sidebarItems = ['overview', 'buttons', 'forms', 'layouts', 'typography'];

  return (
    <div className={`root ${isDarkMode ? 'dark' : 'light'}`}>
      <div className="menu-bar">
        <div className="menu-left">
          {menuItems.map(item => (
            <div
              key={item}
              className={`menu-item ${activeMenu === item ? 'active' : ''}`}
              onClick={() => setActiveMenu(item)}
            >
              {item}
              {activeMenu === item && <div className="menu-item-underline"></div>}
            </div>
          ))}
        </div>
        <div
          className="theme-toggle"
          onClick={() => setIsDarkMode(!isDarkMode)}
        >
          {isDarkMode ? '☀' : '☾'}
        </div>
      </div>

      <div className="layout">
        <div className="sidebar">
          {sidebarItems.map(item => (
            <div
              key={item}
              className={`sidebar-item ${activeSidebar === item ? 'active' : ''}`}
              onClick={() => setActiveSidebar(item)}
            >
              {activeSidebar === item && <span className="dot"></span>}
              {item}
            </div>
          ))}
        </div>

        <div className="main-content">
          <div className="title">
            Components
            <span className="badge">new</span>
          </div>
          <div className="subtitle">A minimal interface with subtle accent colors</div>

          <div className="grid">
            <div className="card">
              <div className="card-title">Buttons</div>
              <button
                className="btn"
                onClick={handleButtonClick}
              >
                Primary
              </button>
              <button className="btn btn-secondary">
                Secondary
              </button>
              <button className="btn btn-outline">
                Outline
              </button>
              <button
                className="btn btn-disabled"
                disabled
              >
                Disabled
              </button>
              {statusMessage && (
                <div className={`status status-ok ${isDarkMode ? 'dark' : 'light'}`}>
                  {statusMessage}
                </div>
              )}
            </div>

            <div className="card">
              <div className="card-title">Form Elements</div>
              <input
                type="text"
                placeholder="Text input"
                className="input"
              />
              <select
                className="select"
                value={dropdownValue}
                onChange={(e) => setDropdownValue(e.target.value)}
              >
                <option value="">Select option</option>
                <option value="1">Option 1</option>
                <option value="2">Option 2</option>
                <option value="3">Option 3</option>
              </select>
              {dropdownValue && (
                <div className="note">Selected: Option {dropdownValue}</div>
              )}
            </div>

            <div className="card">
              <div className="card-title">Code Block</div>
              <pre className="pre">
{`const greeting = (name) => {
  return \`Hello, \${name}!\`;
};

greeting('World');`}
              </pre>
            </div>

            <div className="card">
              <div className="card-title">Typography</div>
              <p className="text">
                This is a paragraph with standard text styling. The design focuses on readability and simplicity.
              </p>
              <p className="text-secondary">
                Secondary text uses a lighter color for hierarchy and visual distinction.
              </p>
            </div>

            <div className="card">
              <div className="card-title">Status</div>
              <div className="status-info">
                <span className="status-label">Theme:</span> {isDarkMode ? 'Dark' : 'Light'}
              </div>
              <div className="status-info">
                <span className="status-label">Active:</span> {activeMenu}
              </div>
              <div className="status-info">
                <span className="status-label">Section:</span> {activeSidebar}
              </div>
            </div>

            <div className="card">
              <div className="card-title">Colors</div>
              <div className="color-swatches">
                <div className="color-swatch primary"></div>
                <div className="color-swatch accent"></div>
              </div>
              <div className="color-info">
                Primary: #80b7ff<br/>
                Accent: #f28478
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export { App };