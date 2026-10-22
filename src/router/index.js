import { createRouter, createWebHashHistory } from 'vue-router';
import ExploreView from '@/views/ExploreView.vue';
import PlanView from '@/views/PlanView.vue';
import ProfileView from '@/views/ProfileView.vue';

const routes = [
  {
    path: '/',
    redirect: '/explore'
  },
  {
    path: '/explore',
    name: 'explore',
    component: ExploreView
  },
  {
    path: '/plan',
    name: 'plan',
    component: PlanView
  },
  {
    path: '/profile',
    name: 'profile',
    component: ProfileView
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  }
});

export default router;
