import prettier from 'eslint-config-prettier';
import js from '@eslint/js';
import { includeIgnoreFile } from '@eslint/compat';
import svelte from 'eslint-plugin-svelte';
import globals from 'globals';
import { fileURLToPath } from 'node:url';
import ts from 'typescript-eslint';
import svelteConfig from './svelte.config.js';

const gitignorePath = fileURLToPath(new URL('./.gitignore', import.meta.url));

export default ts.config(
	includeIgnoreFile(gitignorePath),
	js.configs.recommended,
	...ts.configs.recommended,
	...svelte.configs.recommended,
	prettier,
	...svelte.configs.prettier,
	{
		languageOptions: {
			globals: {
				...globals.browser,
				...globals.node
			}
		}
	},
	{
		files: ['**/*.svelte', '**/*.svelte.ts', '**/*.svelte.js'],
		ignores: ['eslint.config.js', 'svelte.config.js', 'openapi-ts.config.ts'],

		languageOptions: {
			parserOptions: {
				projectService: true,
				extraFileExtensions: ['.svelte'],
				parser: ts.parser,
				svelteConfig
			}
		}
	},
	{
		curly: ['error', 'all'],
		'brace-style': ['error', '1tbs'],
		indent: ['error', 2],
		quotes: ['error', 'single', { avoidEscape: true }],
		'no-unused-vars': ['error', { argsIgnorePattern: '^_' }],

		'@typescript-eslint/explicit-function-return-type': ['warn'],
		'@typescript-eslint/explicit-module-boundary-types': ['warn'],
		'@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],

		'key-spacing': ['error', { beforeColon: false, afterColon: true }],
		'keyword-spacing': ['error', { before: true, after: true }],
		'space-before-blocks': ['error', 'always'],
		'space-before-function-paren': [
			'error',
			{ anonymous: 'always', named: 'never', asyncArrow: 'always' }
		],
		'space-in-parens': ['error', 'never'],
		'space-infix-ops': 'error',
		'object-curly-spacing': ['error', 'always']
	}
);
