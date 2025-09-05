import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
  {
    files: ['**/*.vue', '**/*.{ts,js,mjs,cjs}'],
    rules: {
      // Vue specific rules
      'vue/html-self-closing': ['error', { 'html': { 'void': 'always' } }],
      'vue/v-on-event-hyphenation': ['error', 'never'],
      'vue/no-unused-vars': ['error', { 'ignorePattern': '^_' }],
      'vue/multi-word-component-names': 0,
      'vue/attribute-hyphenation': 0,
      "vue/prop-name-casing": ["error", "camelCase"],

      // TypeScript specific rules
      '@typescript-eslint/ban-ts-comment': 0,
      '@typescript-eslint/no-explicit-any': 0,
      '@typescript-eslint/no-extraneous-class': 0, // Classes with only static members are allowed
      '@typescript-eslint/prefer-literal-enum-member': 0,

      // General rules
      'no-extra-boolean-cast': 0, // Allow !! to convert to boolean
    },
  }
)
