import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/stitch-tokens.css'
import { initAgentFeedbackExtensions } from './debug/setupAgentFeedback.js'
import { IS_DEBUG_BUILD, APP_VERSION } from './config/version.js'

if (typeof window !== 'undefined') {
  window.__ALPINE_VERSION__ = { version: APP_VERSION, versionTag: `v${APP_VERSION}` };
}

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

if (import.meta.env.DEV || IS_DEBUG_BUILD) {
  initAgentFeedbackExtensions(pinia)
}

app.mount('#app')
