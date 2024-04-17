const _FRONT_SCHEME = "http";
const _FRONT_HOST = "localhost";
const _FRONT_PORT = "3000";
export const _FRONT_URL = `${_FRONT_SCHEME}://${_FRONT_HOST}:${_FRONT_PORT}`;

const _BACK_SCHEME = "http";
const _BACK_HOST = "localhost";
const _BACK_PORT = "8000";
export const _BACK_URL = `${_BACK_SCHEME}://${_BACK_HOST}:${_BACK_PORT}`;

export const urls = {
  dashboard: `${_FRONT_URL}/`,
  login: `${_FRONT_URL}/login`,
  profile: `${_FRONT_URL}/profile`,
  timeline: `${_FRONT_URL}/timeline`,
};

export const apis = {
  login: `${_BACK_URL}/users/login/`,
  profile: `${_BACK_URL}/users/dashboard/`,
  timeline: `${_BACK_URL}/users/timeline/`,
  userData: `${_BACK_URL}/users/`,
  notFound: `${_BACK_URL}/static/not_found.png/`
};
