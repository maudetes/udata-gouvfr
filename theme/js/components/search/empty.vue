<!--
Nothing to see here ! Well actually it's a small component that says this.
-->

<template>
  <div
    class="search-empty bg-grey-50 p-lg my-md pb-hg"
    :class="{ 'row-inline': wide }"
  >
    <div :class="{ 'pr-lg': wide }" v-html="Empty" />
    <div :class="{ 'mt-lg': !wide }">
      <h4>
        <span v-text='$t("There are no results for your search")'></span>
      </h4>
      <p>
        <span v-text='copy'></span>
        <span v-if="queryString">{{ `"${queryString}"` }}</span>
      </p>
      <p v-if="copyAfter"><span v-text='copyAfter'></span></p>
      <a class="nav-link mt-md" @click="onClick" v-if="onClick"><span v-text='cta'></span></a>
      <a class="nav-link mt-md" :href="link" v-else><span v-text='cta'></span></a>
    </div>
  </div>
</template>

<script>
import Empty from "svg/search/empty.svg";

export default {
  props: {
    queryString: String,
    cta: String,
    copy: String,
    copyAfter: String,
    link: String,
    onClick: Function,
    wide: Boolean,
  },
  data() {
    return {
      Empty,
    };
  },
};
</script>
