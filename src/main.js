import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './styles/stitch-tokens.css'
import { initAgentFeedbackExtensions } from './debug/setupAgentFeedback.js'
import { IS_DEBUG_BUILD } from './config/version.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

if (import.meta.env.DEV || IS_DEBUG_BUILD) {
  initAgentFeedbackExtensions(pinia)
}

app.mount('#app')
