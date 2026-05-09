// Commitlint-Konfiguration. Erlaubte Typen aus project-context.md Abschnitt 7.
// Conventional-Commits-Basis-Regelset, mit eingeschränkter Typ-Liste.

/** @type {import('@commitlint/types').UserConfig} */
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      ["feat", "fix", "refactor", "docs", "test", "chore", "perf", "build", "ci", "init"],
    ],
    "subject-case": [2, "never", ["start-case", "pascal-case", "upper-case"]],
    "header-max-length": [2, "always", 100],
  },
};
