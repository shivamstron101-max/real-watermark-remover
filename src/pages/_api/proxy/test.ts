import type { APIRoute } from 'astro';

export const prerender = false;

const BACKEND_URL = 'https://shivamstron304--watermark-remover-v3-web.modal.run/test-post';

export const POST: APIRoute = async () => {
    try {
        const response = await fetch(BACKEND_URL, { method: 'POST' });
        const data = await response.json();
        return new Response(JSON.stringify(data), { 
            status: 200,
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (e) {
        return new Response(JSON.stringify({ error: 'Test POST failed' }), { 
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
};
