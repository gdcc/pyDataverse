// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightThemeObsidian from 'starlight-theme-obsidian'
import starlightHeadingBadges from 'starlight-heading-badges'
import mermaid from 'astro-mermaid';


// https://astro.build/config
export default defineConfig({
	site: 'https://gdcc.github.io',
	base: '/pyDataverse',
	redirects: {
		'/': '/getting-started',
	},
	integrations: [
		mermaid(
			{
				theme: 'forest',
				autoTheme: true,
				mermaidConfig: {
					flowchart: {
						curve: 'basis'
					}
				},
			}
		),
		starlight({
			title: 'pyDataverse',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/gdcc/pyDataverse' }],
			plugins: [starlightHeadingBadges(), starlightThemeObsidian(
				{
					backlinks: false,
					graph: false
				}
			)],
			sidebar: [
				{
					label: "Getting Started",
					items: [
						{ label: "Overview", slug: "getting-started" },
						{ label: "Installation", slug: "installation" },
					],
				},
				{
					label: 'High-level API',
					badge: 'New',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'high-level/concept' },
						{ label: 'Connecting to a Dataverse', slug: 'high-level/dataverse' },
						{ label: 'Working with Collections', slug: 'high-level/collection' },
						{ label: 'Working with Datasets', slug: 'high-level/dataset' },
						{ label: 'Working with Files', slug: 'high-level/file' },
						{ label: 'Searching for Content', slug: 'high-level/search' },
					],
				},
				{
					label: 'Dataverse APIs',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'apis/overview' },
						{ label: 'Native API', slug: 'apis/native' },
						{ label: 'Semantic API', slug: 'apis/semantic' },
						{ label: 'Search API', slug: 'apis/search' },
						{ label: 'Data Access API', slug: 'apis/data-access' },
						{ label: 'Metrics API', slug: 'apis/metrics' },
					],
				},
				{
					label: 'Filesystem',
					badge: 'New',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'filesystem/overview' },
						{ label: 'Connecting', slug: 'filesystem/connecting' },
						{ label: 'Browsing & Metadata', slug: 'filesystem/browsing' },
						{ label: 'Reading Files', slug: 'filesystem/reading' },
						{ label: 'Writing Files', slug: 'filesystem/writing' },
						{ label: 'Tabular Data', slug: 'filesystem/tabular' },
						{ label: 'pandas & fsspec', slug: 'filesystem/pandas' },
					],
				},
				{
					label: 'MCP',
					badge: 'New',
					collapsed: true,
					items: [
						{ label: 'Overview', slug: 'mcp/overview' },
						{ label: 'Available Tools', slug: 'mcp/tools' },
						{ label: 'Creating a Server', slug: 'mcp/server' },
					],
				},
				{
					label: 'Resources',
					collapsed: true,
					items: [
						{ label: 'The Dataverse Project', link: "https://dataverse.org/" },
						{ label: 'PyDataverse Cookbook', link: "https://github.com/gdcc/dataverse-recipes/tree/main/python" },
						{ label: 'Dataverse API Reference', link: "https://guides.dataverse.org/en/latest/api/index.html" },
					]
				},
			],
		}),
	],
});
