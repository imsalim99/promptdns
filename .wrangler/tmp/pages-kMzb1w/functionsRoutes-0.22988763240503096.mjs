import { onRequestPost as __api_auth_logout_ts_onRequestPost } from "C:\\Users\\imsalim\\.zcode\\workspace\\default\\promptdns\\functions\\api\\auth\\logout.ts"
import { onRequestPost as __api_auth_magic_link_ts_onRequestPost } from "C:\\Users\\imsalim\\.zcode\\workspace\\default\\promptdns\\functions\\api\\auth\\magic-link.ts"
import { onRequestGet as __api_auth_verify_ts_onRequestGet } from "C:\\Users\\imsalim\\.zcode\\workspace\\default\\promptdns\\functions\\api\\auth\\verify.ts"
import { onRequestDelete as __api_domains_ts_onRequestDelete } from "C:\\Users\\imsalim\\.zcode\\workspace\\default\\promptdns\\functions\\api\\domains.ts"
import { onRequestGet as __api_domains_ts_onRequestGet } from "C:\\Users\\imsalim\\.zcode\\workspace\\default\\promptdns\\functions\\api\\domains.ts"
import { onRequestPost as __api_domains_ts_onRequestPost } from "C:\\Users\\imsalim\\.zcode\\workspace\\default\\promptdns\\functions\\api\\domains.ts"

export const routes = [
    {
      routePath: "/api/auth/logout",
      mountPath: "/api/auth",
      method: "POST",
      middlewares: [],
      modules: [__api_auth_logout_ts_onRequestPost],
    },
  {
      routePath: "/api/auth/magic-link",
      mountPath: "/api/auth",
      method: "POST",
      middlewares: [],
      modules: [__api_auth_magic_link_ts_onRequestPost],
    },
  {
      routePath: "/api/auth/verify",
      mountPath: "/api/auth",
      method: "GET",
      middlewares: [],
      modules: [__api_auth_verify_ts_onRequestGet],
    },
  {
      routePath: "/api/domains",
      mountPath: "/api",
      method: "DELETE",
      middlewares: [],
      modules: [__api_domains_ts_onRequestDelete],
    },
  {
      routePath: "/api/domains",
      mountPath: "/api",
      method: "GET",
      middlewares: [],
      modules: [__api_domains_ts_onRequestGet],
    },
  {
      routePath: "/api/domains",
      mountPath: "/api",
      method: "POST",
      middlewares: [],
      modules: [__api_domains_ts_onRequestPost],
    },
  ]