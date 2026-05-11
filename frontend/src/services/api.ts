type RequestBody = BodyInit | Record<string, unknown> | undefined;

const UNSAFE_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(status: number, message: string, details: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

function getCookie(name: string) {
  const value = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`));

  return value ? decodeURIComponent(value.split('=')[1]) : '';
}

function buildBody(body: RequestBody) {
  if (!body || body instanceof FormData) {
    return body;
  }

  return JSON.stringify(body);
}

function buildHeaders(method: string, body: RequestBody) {
  const headers = new Headers({
    Accept: 'application/json',
  });

  if (body && !(body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (UNSAFE_METHODS.has(method)) {
    const csrfToken = getCookie('csrftoken');

    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken);
    }
  }

  return headers;
}

export async function apiRequest<T>(
  path: string,
  options: { method?: string; body?: RequestBody } = {},
) {
  const method = options.method ?? 'GET';
  const response = await fetch(`/api${path}`, {
    method,
    credentials: 'same-origin',
    headers: buildHeaders(method, options.body),
    body: buildBody(options.body),
  });

  const isJson = response.headers
    .get('content-type')
    ?.includes('application/json');
  const data = isJson ? await response.json() : null;

  if (!response.ok) {
    throw new ApiError(response.status, response.statusText, data);
  }

  return data as T;
}
