<template>
  <j-tray-plugin
    description='Download a data product from the Skyview Archive'
    :link="'https://skyview.gsfc.nasa.gov/current/cgi/titlepage.pl'"
    :popout_button="popout_button">

    <j-plugin-section-header>Survey Collections</j-plugin-section-header>
      <v-row>
        <v-select
          :menu-props="{ left: true }"
          attach
          :items="survey_collections"
          @change="collection_selected"
          label="Available Collections"
          hint="Select a survey collection to filter your surveys"
          persistent-hint
        ></v-select>
      </v-row>

      <v-row>
        <v-select
          :menu-props="{ left: true }"
          attach
          :items="surveys"
          @change="survey_selected"
          label="Available Surveys"
          hint="Select a survey to query"
          persistent-hint
        ></v-select>
      </v-row>

    <j-plugin-section-header>Source Selection</j-plugin-section-header>

      <v-row>
          <v-text-field
          v-model="source"
          label="Source or Coordinates"
          hint="Enter a source name or Coordinates to center your query on"
          persistent-hint>
          </v-text-field>
      </v-row>

    <j-plugin-section-header>Common Options</j-plugin-section-header>

      <v-row>
        <v-text-field
        v-model.number="resolution_pix"
        type="number"
        label="Resolution"
        hint="Minimum resolution in pixels"
        persistent-hint>
        </v-text-field>
      </v-row>

      <v-row>
        <v-text-field
        v-model.number="radius_deg"
        type="number"
        label="Radius"
        hint="Angular radius of the specified field in degrees"
        persistent-hint>
        </v-text-field>
      </v-row>

    <v-row class="row-no-outside-padding">
        <v-col>
            <v-btn color="primary" text @click="submit_request">Search SkyView</v-btn>
        </v-col>
    </v-row>

  </j-tray-plugin>
</template>