import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
	input: "./openapi.json",
	output: "./src/api-client/",
	plugins: [
		"@hey-api/client-axios",
		"@hey-api/sdk",
		"@hey-api/schemas",
		"@hey-api/typescript"
  ]
});
