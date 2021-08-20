<!-- This is similar to the Jinja2 `dataset/search-result.html` template but in
Vue. -->

<template>
  <article class="dataset-card dataset-search-result">
    <div class="card-logo" v-if="organization">
      <Placeholder
        type="dataset"
        :src="organization.logo_thumbnail"
        :alt="organization.name"
      />
    </div>
    <div class="card-logo" v-else-if="owner">
      <Placeholder
        type="dataset"
        :src="owner.logo_thumbnail"
        :alt="owner.name"
      />
      <div class="logo-badge">
        <span v-html="private" v-if="private" />
        <span v-html="certified" v-else-if="organization?.public_service" />
      </div>
    </div>
    <div class="card-logo" v-else>
      <Placeholder type="dataset" />
    </div>
    <div class="card-data">
      <h4 class="card-title"><span v-text='title'></span></h4>
      <div class="card-description text-grey-300 mt-xs">
        <span v-text='$filters.excerpt(description)'></span>
      </div>
    </div>
    <dl class="card-hover">
      <div v-if="temporal_coverage">
        <dt><span v-text='$t("Temporal coverage")'></span></dt>
        <dd><span v-text='Object.values(temporal_coverage).join(" - ")'></span></dd>
      </div>
      <div v-if="frequency">
        <dt><span v-text='$t("Frequency")'></span></dt>
        <dd><span v-text='frequency'></span></dd>
      </div>
      <div v-if="geozone">
        <dt><span v-text='$t("Spatial coverage")'></span></dt>
        <dd><span v-text='geozone.join(", ")'></span></dd>
      </div>
      <div v-if="spatial?.granularity">
        <dt><span v-text='$t("Territorial coverage granularity")'></span></dt>
        <dd><span v-text='spatial.granularity'></span></dd>
      </div>
    </dl>
    <ul class="card-footer">
      <li>
        <strong><span v-text='resources.length || 0'></span></strong>
        <span v-text='$tc("resources", resources.length || 0)'></span>
      </li>
      <li>
        <strong><span v-text='metrics.reuses || 0'></span></strong>
        <span v-text='$tc("reuses", metrics.reuses || 0)'></span>
      </li>
      <li>
        <strong><span v-text='metrics.followers || 0'></span></strong>
        <span v-text='$tc("favourites", metrics.followers || 0)'></span>
      </li>
    </ul>
  </article>
</template>

<script>
import Placeholder from "../utils/placeholder";
import certified from "svg/certified.svg";
import private from "svg/private.svg";

export default {
  props: {
    title: String,
    image_url: String,
    organization: Object,
    owner: Object,
    description: String,
    temporal_coverage: String,
    frequency: String,
    spatial: Object,
    metrics: Object,
    resources: Array,
    private: Boolean,
  },
  components: {
    Placeholder,
  },
  data() {
    return {
      geozone: null,
    };
  },
  async mounted() {
    this.certified = certified;
    this.private = private;
    //Fetching geozone names on load (they're not included in the dataset object)

    const zones = this?.spatial?.zones;
    if (zones) {
      let promises = zones.map((zone) =>
        this.$api
          .get("spatial/zone/" + zone)
          .then((resp) => resp.data)
          .then((obj) => obj && obj?.properties?.name)
      );

      this.geozone = await Promise.all(promises);
    }
  },
};
</script>
