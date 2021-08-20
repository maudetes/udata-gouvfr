import { createApp } from "vue";

import Threads from "./components/discussions/threads.vue";
import Suggest from "./components/search/suggest-box";
import Search from "./components/search/search";
import FollowButton from "./components/utils/follow-button";

import Tabs from "./components/vanilla/tabs";
import Accordion from "./components/vanilla/accordion";
import Clipboard from "./components/vanilla/clipboard";

import VueFinalModal from "vue-final-modal";
import Toaster from "@meforma/vue-toaster";

import Api from "./plugins/api";
import Auth from "./plugins/auth";
import Modals from "./plugins/modals";
import i18n from "./plugins/i18n";
import bodyClass from "./plugins/bodyClass";
import filters from "./plugins/filters";

import InitSentry from "./sentry";

mountComponents = [
  ["#discussion-threads", "discussion-threads", Threads],
  ["#header", "suggest", Suggest],
  ["#search", "search", Search],
  ["#follow", "follow-button", FollowButton]
]

for (var comp of mountComponents) {

  app = createApp({});

  // Configure as early as possible in the app's lifecycle
  InitSentry(app);

  app.use(Api);
  app.use(Auth);
  app.use(VueFinalModal());
  app.use(Modals); //Has to be loaded after VueFinalModal
  app.use(i18n);
  app.use(bodyClass);
  app.use(filters);
  app.use(Toaster);

  app.component(comp[1], comp[2]);
  app.mount(comp[0]);
  console.log("JS is injected for component: " + comp[1]);
}
