import React, { useState } from 'react'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [darkMode, setDarkMode] = useState(false)
  const [activityFeed, setActivityFeed] = useState([])
  const [formData, setFormData] = useState({})

  const navigateTo = (page) => {
    setCurrentPage(page)
    addActivity(`Navigated to ${page}`)
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    addActivity(`Toggled ${!darkMode ? 'dark' : 'light'} mode`)
  }

  const addActivity = (message) => {
    setActivityFeed(prev => [...prev, { message, timestamp: new Date().toLocaleTimeString() }])
  }

  const runFileFlow = async () => {
    addActivity('Running File Flow...')
    try {
      // Call the Python backend API
      const response = await window.electronAPI.callPythonAPI('/fileflow/process', {
        source_path: '/path/to/source',
        destination_path: '/path/to/destination'
      })
      addActivity('File Flow completed successfully')
    } catch (error) {
      addActivity('File Flow failed: ' + error.message)
    }
  }

  const openZohoForm = () => {
    addActivity('Opening Zoho form...')
    // Open the Zoho form in a new window or iframe
    window.open('https://writer.zohopublic.com/writer/published/k8rb3640aae6022414281b9c872cd3e644c98/fill', '_blank')
  }

  const submitForm = async () => {
    addActivity('Submitting form...')
    try {
      const response = await window.electronAPI.callPythonAPI('/forms/submit', {
        form_data: formData,
        form_type: 'zoho_fillable',
        user_id: 'user_123'
      })
      addActivity('Form submitted successfully')
    } catch (error) {
      addActivity('Form submission failed: ' + error.message)
    }
  }

  const saveFormDraft = async () => {
    addActivity('Saving form draft...')
    try {
      // Save draft functionality
      addActivity('Form draft saved')
    } catch (error) {
      addActivity('Failed to save draft: ' + error.message)
    }
  }

  const exportFormPDF = async () => {
    addActivity('Exporting form to PDF...')
    try {
      const response = await window.electronAPI.callPythonAPI('/forms/export-pdf', formData)
      addActivity('Form exported to PDF successfully')
    } catch (error) {
      addActivity('PDF export failed: ' + error.message)
    }
  }

  return (
    <div className={`app ${darkMode ? 'dark-mode' : 'light-mode'}`}>
      <aside className="sidebar">
        <div className="logo">
          <img src="/assets/qlife-DNKpKEwB.png" alt="QiLife Logo" />
          <h2>QiLife</h2>
        </div>
        <nav>
          <button onClick={() => navigateTo('dashboard')}>Dashboard</button>
          <button onClick={() => navigateTo('quick-receipt')}>Quick Receipt</button>
          <button onClick={() => navigateTo('file-flow')}>File Flow</button>
          <button onClick={() => navigateTo('forms')}>Forms</button>
          <button onClick={() => navigateTo('settings')}>Settings</button>
          <button onClick={toggleDarkMode}>Toggle Dark Mode</button>
        </nav>
        <div className="activity-feed">
          <div className="feed-header">
            <span>Activity Feed</span>
          </div>
          <ul>
            {activityFeed.map((activity, index) => (
              <li key={index}>
                <span className="time">{activity.timestamp}</span>
                <span className="message">{activity.message}</span>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      <main>
        {currentPage === 'dashboard' && (
          <section className="page active">
            <h1>Command Dashboard</h1>
            <p>Home &gt; Dashboard</p>
            <p>Welcome to QiLife Cockpit.</p>
          </section>
        )}

        {currentPage === 'quick-receipt' && (
          <section className="page">
            <h1>Quick Receipt</h1>
            <div className="receipt-entry">
              <input placeholder="Item Name" />
              <input type="number" placeholder="Quantity" />
              <input type="number" step="0.01" placeholder="Price" />
              <textarea placeholder="Notes (optional)"></textarea>
              <button>Add Item</button>
              <button>Print Receipt</button>
            </div>
            <div className="receipt-preview"></div>
          </section>
        )}

        {currentPage === 'file-flow' && (
          <section className="page">
            <h1>File Flow</h1>
            <p>Home &gt; File Flow</p>
            <pre>Running File Flow...</pre>
            <button onClick={runFileFlow}>Run File Flow</button>
          </section>
        )}

        {currentPage === 'forms' && (
          <section className="page">
            <h1>Forms & Documents</h1>
            <p>Home &gt; Forms</p>
            
            <div className="forms-container">
              <div className="form-card">
                <h3>Zoho Fillable Form</h3>
                <p>Access your embedded Zoho form for document processing.</p>
                <button onClick={openZohoForm} className="form-button">
                  Open Zoho Form
                </button>
              </div>

              <div className="form-embed">
                <h3>Embedded Form View</h3>
                <div className="iframe-container">
                  <iframe 
                    src="https://writer.zohopublic.com/writer/published/k8rb3640aae6022414281b9c872cd3e644c98/fill"
                    title="Zoho Form"
                    width="100%"
                    height="600px"
                    frameBorder="0"
                    allowFullScreen
                  />
                </div>
              </div>

              <div className="form-actions">
                <h3>Form Actions</h3>
                <div className="action-buttons">
                  <button onClick={submitForm}>
                    Submit Form
                  </button>
                  <button onClick={saveFormDraft}>
                    Save Draft
                  </button>
                  <button onClick={exportFormPDF}>
                    Export PDF
                  </button>
                </div>
              </div>
            </div>
          </section>
        )}

        {currentPage === 'settings' && (
          <section className="page">
            <h1>Settings</h1>
            <p>Home &gt; Settings</p>
            <div className="settings-group">
              <label>OpenAI API Key</label>
              <input type="password" />
            </div>
            <div className="settings-group">
              <label>Gemini API Key</label>
              <input type="password" />
            </div>
            <div className="settings-group">
              <label>Twilio API Key</label>
              <input type="password" />
            </div>
            <div className="settings-group">
              <label>Zoho Form URL</label>
              <input 
                type="text" 
                defaultValue="https://writer.zohopublic.com/writer/published/k8rb3640aae6022414281b9c872cd3e644c98/fill"
                placeholder="Enter your Zoho form URL"
              />
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App 