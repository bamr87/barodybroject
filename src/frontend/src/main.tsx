import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import './styles.css'

import { App } from './App'

const container = document.getElementById('root')
if (!container) throw new Error('#root is missing from the page shell')

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
