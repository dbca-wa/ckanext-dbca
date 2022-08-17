ckan.module("dbca-spatial-form", function ($, _) {
  "use strict";
  return {
    options: {
      table: '<table class="table table-striped table-bordered table-condensed"><tbody>{body}</tbody></table>',
      row: '<tr><th>{key}</th><td>{value}</td></tr>',
      i18n: {
      },
      style: {
        color: '#F06F64',
        weight: 2,
        opacity: 1,
        fillColor: '#F06F64',
        fillOpacity: 0.1,
        clickable: false
      },
      default_extent: [[-10, 130], [-40, 110]]
    },
    initialize: function () {      
      this.map_id = this.el.data('map-id');
      

      // hack to make leaflet use a particular location to look for images
      //L.Icon.Default.imagePath = this.options.site_url + 'js/vendor/leaflet/images';

      this.extent = this.el.data('extent');
      if (extent){
        if (extent instanceof Array) {
          // Assume it's a pair of coords like [[90, 180], [-90, -180]]
          this.options.default_extent = user_default_extent;
        } else if (extent instanceof Object) {
          // Assume it's a GeoJSON bbox
          this.options.default_extent = new L.GeoJSON(extent).getBounds();
        }
      }


      jQuery.proxyAll(this, /_on/);
      this.el.ready(this._onReady);
    },

    _onReady: function(){
      
      var map, backgroundLayer, oldExtent, drawnItems, ckanIcon;
      var ckanIcon = L.Icon.extend({options: this.options.style});


      /* Initialise basic map */
      var map = ckan.commonLeafletMap(
          this.map_id,
          this.options.map_config,
          {
            attributionControl: false,
            drawControlTooltips: true
          }
      );
      map.fitBounds(this.options.default_extent);

      /* Add an empty layer for newly drawn items */
      var drawnItems = new L.FeatureGroup();
      map.addLayer(drawnItems);


      /* Add GeoJSON layers for any GeoJSON resources of the dataset */
      //var existingLayers = {};
      // var url = window.location.href.split('dataset/edit/');
      // $.ajax({
      //  url: url[0] + 'api/3/action/package_show',
      //  data: {id : url[1]},
      //  dataType: 'jsonp',
      //  success: function(data) {
      //    //console.log('Got resources: ' + JSON.stringify(data.result.resources));
      //    var r = data.result.resources;
      //    for (i in r){
      //     if (r[i].format == 'GeoJSON'){
      //      //console.log('Found GeoJSON for ' + r[i].name + ' with id ' + r[i].id);   
           
      //      /* Option 1: Load GeoJSON using leaflet.ajax */
      //      //var geojsonLayer = L.geoJson.ajax(r[id].url);
      //      //geojsonLayer.addTo(map);

      //      /* Option 2: Load GeoJSON using JQuery */
      //      $.getJSON(r[i].url, function(data) {
      //         var gj = L.geoJson(data, {
      //             pointToLayer: function (feature, latLng) {
      //                 return new L.Marker(latLng, {icon: new ckanIcon})
      //             },
      //             onEachFeature: function(feature, layer) {
      //               var body = '';
      //               var row = '<tr><th>{key}</th><td>{value}</td></tr>';
      //               var table = '<table class="table table-striped table-bordered table-condensed" style="width:300px;"><tbody>{body}</tbody></table>';
      //               jQuery.each(feature.properties, function(key, value){
      //                 if (value != null && typeof value === 'object') {
      //                   value = JSON.stringify(value);
      //                 }
      //                 body += L.Util.template(row, {key: key, value: value});
      //               });
      //               var popupContent = L.Util.template(table, {body: body});
      //                 layer.bindPopup(popupContent);
      //             }
      //         });
      //         gj.addTo(map);
      //         //existingLayers[r[i].name] = gj;
      //      }); // end getJSON
      //     } // end if
      //    } // end for
      //    //L.control.layers(existingLayers).addTo(map); // or similar
      //  }
      //  });

      /* Add existing extent or new layer */
      if (this.extent) {
          /* update = show existing polygon */
          oldExtent = L.geoJson(this.extent, {
            style: this.options.style,
            pointToLayer: function (feature, latLng) {
              return new L.Marker(latLng, {icon: new ckanIcon})
            }
          });
          oldExtent.addTo(map);
          map.fitBounds(oldExtent.getBounds());
      }


      /* Leaflet.draw: add drawing controls for drawnItems */
      var drawControl = new L.Control.Draw({
          draw: {
              polyline: false,
              circle: false,
              marker: false,
              rectangle: {repeatMode: false}

          },
          edit: { featureGroup: drawnItems }
      });
      map.addControl(drawControl);


      /* Aggregate all features in a FeatureGroup into one MultiPolygon, 
       * update inputid with that Multipolygon's geometry 
       */
      var featureGroupToInput = function(fg, input){
          var gj = drawnItems.toGeoJSON().features;
          var polyarray = [];
          $.each(gj, function(index, value){ polyarray.push(value.geometry.coordinates); });
          mp = {"type": "MultiPolygon", "coordinates": polyarray};
          // TODO use input for element id
          $('#field-spatial').val(JSON.stringify(mp));
          //$("#" + input).val(JSON.stringify(mp)); // doesn't work
      };


      /* When one shape is drawn/edited/deleted, update input_id with all drawn shapes */
      map.on('draw:created', function (e) {
          var type = e.layerType,
              layer = e.layer;
          drawnItems.addLayer(layer);
          // To only add the latest drawn element to input #field-spatial:
          //$("#field-spatial")[0].value = JSON.stringify(e.layer.toGeoJSON().geometry);
          featureGroupToInput(drawnItems, this.input);
      });

      map.on('draw:editstop', function(e){
          featureGroupToInput(drawnItems, this.input);
      });

      map.on('draw:deletestop', function(e){
          featureGroupToInput(drawnItems, this.input);
      });

  }
  };
});
