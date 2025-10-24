import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
	devIndicators: false,
	webpack: (config) => {
		config.resolve = config.resolve || {};
		config.resolve.alias = {
			...(config.resolve.alias || {}),
			"@": path.resolve(__dirname, "src"),
		};
		return config;
	},
};

export default nextConfig;
