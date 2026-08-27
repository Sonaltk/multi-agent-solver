export default [
  {
    files: ["**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs"],
    rules: {
      "no-unused-vars": "warn",
      "no-undef": "error",
      "no-unreachable": "error",
      "no-constant-condition": "warn",
      "eqeqeq": "warn",
    },
  },
];