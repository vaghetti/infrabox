<template>
    <div class="m-sm full-height">
        <md-card md-theme="white" class="full-height clean-card">
            <md-card-header>
                <md-card-header-text class="setting-list">
                    <md-icon>security</md-icon>
                    <span>Badges</span>
                </md-card-header-text>
            </md-card-header>

            <md-card-area>
                <md-list class="m-b-md">
                    <md-list-item class="m-r-xl">
                        <div>
                            <img :src="buildState" />
                            <pre>[![Build Status]({{ api_host }}/../v1/projects/{{ project.id }}/state.svg)]({{ dashboard_host }}/dashboard/#/project/{{ project.name }})</pre>
                        </div>
                    </md-list-item>
                    <md-list-item class="m-r-xl">
                        <div>
                            <img :src="testState" />
                            <pre>[![Test Status]({{ api_host }}/../v1/projects/{{ project.id }}/tests.svg)]({{ dashboard_host }}/dashboard/#/project/{{ project.name }})</pre>
                        </div>
                    </md-list-item>
                </md-list>
            </md-card-area>
        </md-card>
    </div>
</template>

<script>
import store from '../../store'

export default {
    props: ['project'],
    created () {
        this.api_host = store.state.settings.INFRABOX_API_URL
        this.dashboard_host = store.state.settings.INFRABOX_DASHBOARD_URL
        this.buildState = `${this.api_host}/../v1/projects/${this.project.id}/state.svg`
        this.testState = `${this.api_host}/../v1/projects/${this.project.id}/tests.svg`
    }
}
</script>
