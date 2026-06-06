import type { APIRoute } from 'astro';

export const prerender = false;

const BACKEND_URL = 'https://shivamstron304--watermark-remover-v3-web.modal.run/api/proxy';

export const POST: APIRoute = async ({ request }) => {
    try {
        console.log('Proxying main process request to:', BACKEND_URL);
        
        const contentType = request.headers.get('content-type');
        
        // Use the raw request body stream for efficiency
        // Node's fetch requires 'duplex: half' when sending a stream
        const fetchOptions: any = {
            method: 'POST',
            body: request.body,
            headers: contentType ? { 'Content-Type': contentType } : {},
            duplex: 'half'
        };

        const response = await fetch(BACKEND_URL, fetchOptions);

        if (!response.ok) {
            const errorText = await response.text();
            console.error('Backend returned error:', errorText);
            return new Response(JSON.stringify({ error: `Backend error: ${errorText}` }), { 
                status: response.status,
                headers: { 'Content-Type': 'application/json' }
            });
        }

        const blob = await response.blob();
        return new Response(blob, {
            status: 200,
            headers: {
                'Content-Type': 'image/jpeg',
            },
        });
    } catch (error) {
        console.error('Proxy Error:', error);
        return new Response(JSON.stringify({ error: `Proxy internal error: ${error.message}` }), { 
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        });
    }
};
