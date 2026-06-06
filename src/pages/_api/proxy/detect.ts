import type { APIRoute } from 'astro';

export const prerender = false;

const BACKEND_URL = 'https://shivamstron304--watermark-remover-v3-web.modal.run/detect';

export const POST: APIRoute = async ({ request }) => {
    try {
        const contentType = request.headers.get('content-type');
        
        const fetchOptions: any = {
            method: 'POST',
            body: request.body,
            headers: contentType ? { 'Content-Type': contentType } : {},
            duplex: 'half'
        };

        const response = await fetch(BACKEND_URL, fetchOptions);
        const data = await response.json();
        
        return new Response(JSON.stringify(data), { 
            status: response.status,
            headers: { 'Content-Type': 'application/json' }
        });
    } catch (error) {
        console.error('Detect Proxy Error:', error);
        return new Response(JSON.stringify({ error: `Detect internal error: ${error.message}` }), { 
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
};
