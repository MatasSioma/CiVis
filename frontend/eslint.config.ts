import { globalIgnores } from 'eslint/config';
import pluginVue from 'eslint-plugin-vue';
import {
  configureVueProject,
  defineConfigWithVueTs,
  vueTsConfigs,
} from '@vue/eslint-config-typescript';

configureVueProject({
  tsSyntaxInTemplates: true,
  scriptLangs: ['ts'],
});

export default defineConfigWithVueTs(
  pluginVue.configs['flat/essential'],
  vueTsConfigs.recommended,

  globalIgnores(['**/node_modules/**', '**/dist/**', '**/dist-ssr/**']),
);
