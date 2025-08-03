module.exports = {
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.js', '**/tests/**/*.test.ts'],
  collectCoverageFrom: [
    'app/**/*.{js,ts}',
    '!app/**/*.d.ts',
    '!app/main/main.js',
  ],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/app/$1',
  },
}; 