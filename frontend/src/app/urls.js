const _FRONT_SCHEME = "http";
const _FRONT_HOST = "localhost";
const _FRONT_PORT = "3000";
const _FRONT_URL = `${_FRONT_SCHEME}://${_FRONT_HOST}:${_FRONT_PORT}`;

const _BACL_SCHEME = "http";
const _BACL_HOST = "localhost";
const _BACK_PORT = "8000";
export const _BACK_URL = `${_BACL_SCHEME}://${_BACL_HOST}:${_BACK_PORT}`;

export const urls = {
  login: `${_FRONT_URL}/login`,
  profile: `${_FRONT_URL}/profile`,
  timeline: `${_FRONT_URL}/timeline`,
};

export const apis = {
  login: `${_BACK_URL}/users/login/`,
  profile: `${_BACK_URL}/users/dashboard/`,
  timeline: `${_BACK_URL}/users/timeline/`,
};
