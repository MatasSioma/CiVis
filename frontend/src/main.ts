import './assets/css/index.css';

import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);

app.config.errorHandler = (error, instance, info) => {
  console.error('Global Vue Error:', error, info, instance);
};

window.addEventListener('error', (event) => {
  console.error('Window Error:', event.error ?? event.message, event);
});

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise:', event.reason, event);
});

app.use(router);

app.mount('#app');
