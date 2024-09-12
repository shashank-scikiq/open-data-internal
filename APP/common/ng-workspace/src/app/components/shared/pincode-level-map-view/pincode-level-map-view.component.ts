import { Component, OnInit } from '@angular/core';
import * as L from "leaflet";
import * as d3 from "d3";
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';


@Component({
  selector: 'app-pincode-level-map-view',
  templateUrl: './pincode-level-map-view.component.html',
  styleUrl: './pincode-level-map-view.component.scss'
})
export class PincodeLevelMapViewComponent implements OnInit {

  // // Variable to store combined GeoJSON
  // combinedGeoJSON: any = null;
  // map: any;
  // // Define the bounding box for Bangalore (approximate values)
  // minLatitude = 12.7;
  // maxLatitude = 13.2;
  // minLongitude = 77.4;
  // maxLongitude = 77.8;
  // geojsonFiles: any;
  city: string = 'Bangalore';

  constructor(private route: ActivatedRoute) {
    this.route.queryParams.subscribe(params => {
      this.city = params['city'];
    });
  }

  private map: any;
  private minLatitude: any = 12.7;
  private maxLatitude: any = 13.2;
  private minLongitude: any = 77.4;
  private maxLongitude: any = 77.8;
  private combinedGeoJSON: any;
  private geojsonFiles: string[] = [];
  queryParamsSubscription: any;

  ngOnInit(): void {
    console.log("called for ", this.city)
    this.queryParamsSubscription = this.route.queryParams.subscribe(params => {
      // Call your function whenever query params change
      this.setData();
    });
    


  }

  setData() {
    if (this.city == 'Bangalore') {
      this.minLatitude = 12.7;
      this.maxLatitude = 13.2;
      this.minLongitude = 77.4;
      this.maxLongitude = 77.8;
      this.geojsonFiles = ['static/assets/data/pincode-level/bangalore/560001.geojson', 'static/assets/data/pincode-level/bangalore/560002.geojson',
        'static/assets/data/pincode-level/bangalore/560003.geojson', 'static/assets/data/pincode-level/bangalore/560004.geojson', 'static/assets/data/pincode-level/bangalore/560005.geojson',
        'static/assets/data/pincode-level/bangalore/560006.geojson', 'static/assets/data/pincode-level/bangalore/560007.geojson', 'static/assets/data/pincode-level/bangalore/560008.geojson',
        'static/assets/data/pincode-level/bangalore/560009.geojson', 'static/assets/data/pincode-level/bangalore/560010.geojson',
        'static/assets/data/pincode-level/bangalore/560011.geojson', 'static/assets/data/pincode-level/bangalore/560012.geojson', 'static/assets/data/pincode-level/bangalore/560013.geojson',
        'static/assets/data/pincode-level/bangalore/560014.geojson', 'static/assets/data/pincode-level/bangalore/560015.geojson', 'static/assets/data/pincode-level/bangalore/560016.geojson',
        'static/assets/data/pincode-level/bangalore/560017.geojson', 'static/assets/data/pincode-level/bangalore/560018.geojson', 'static/assets/data/pincode-level/bangalore/560019.geojson',
        'static/assets/data/pincode-level/bangalore/560020.geojson', 'static/assets/data/pincode-level/bangalore/560021.geojson', 'static/assets/data/pincode-level/bangalore/560022.geojson',
        'static/assets/data/pincode-level/bangalore/560023.geojson', 'static/assets/data/pincode-level/bangalore/560024.geojson', 'static/assets/data/pincode-level/bangalore/560025.geojson',
        'static/assets/data/pincode-level/bangalore/560026.geojson', 'static/assets/data/pincode-level/bangalore/560027.geojson',
        'static/assets/data/pincode-level/bangalore/560029.geojson', 'static/assets/data/pincode-level/bangalore/560030.geojson',
        'static/assets/data/pincode-level/bangalore/560032.geojson', 'static/assets/data/pincode-level/bangalore/560033.geojson', 'static/assets/data/pincode-level/bangalore/560034.geojson', 'static/assets/data/pincode-level/bangalore/560035.geojson',
        'static/assets/data/pincode-level/bangalore/560036.geojson', 'static/assets/data/pincode-level/bangalore/560037.geojson', 'static/assets/data/pincode-level/bangalore/560038.geojson', 'static/assets/data/pincode-level/bangalore/560039.geojson',
        'static/assets/data/pincode-level/bangalore/560040.geojson', 'static/assets/data/pincode-level/bangalore/560041.geojson', 'static/assets/data/pincode-level/bangalore/560042.geojson', 'static/assets/data/pincode-level/bangalore/560043.geojson',
        'static/assets/data/pincode-level/bangalore/560045.geojson', 'static/assets/data/pincode-level/bangalore/560046.geojson', 'static/assets/data/pincode-level/bangalore/560047.geojson',
        'static/assets/data/pincode-level/bangalore/560048.geojson', 'static/assets/data/pincode-level/bangalore/560049.geojson', 'static/assets/data/pincode-level/bangalore/560050.geojson',

        'static/assets/data/pincode-level/bangalore/560051.geojson', 'static/assets/data/pincode-level/bangalore/560052.geojson', 'static/assets/data/pincode-level/bangalore/560053.geojson', 'static/assets/data/pincode-level/bangalore/560054.geojson',
        'static/assets/data/pincode-level/bangalore/560055.geojson', 'static/assets/data/pincode-level/bangalore/560056.geojson', 'static/assets/data/pincode-level/bangalore/560057.geojson', 'static/assets/data/pincode-level/bangalore/560058.geojson',
        'static/assets/data/pincode-level/bangalore/560059.geojson', 'static/assets/data/pincode-level/bangalore/560060.geojson', 'static/assets/data/pincode-level/bangalore/560061.geojson', 'static/assets/data/pincode-level/bangalore/560062.geojson',
        'static/assets/data/pincode-level/bangalore/560063.geojson', 'static/assets/data/pincode-level/bangalore/560064.geojson', 'static/assets/data/pincode-level/bangalore/560065.geojson', 'static/assets/data/pincode-level/bangalore/560066.geojson',
        'static/assets/data/pincode-level/bangalore/560067.geojson', 'static/assets/data/pincode-level/bangalore/560068.geojson', 'static/assets/data/pincode-level/bangalore/560069.geojson', 'static/assets/data/pincode-level/bangalore/560070.geojson',
        'static/assets/data/pincode-level/bangalore/560071.geojson', 'static/assets/data/pincode-level/bangalore/560072.geojson', 'static/assets/data/pincode-level/bangalore/560073.geojson', 'static/assets/data/pincode-level/bangalore/560074.geojson',
        'static/assets/data/pincode-level/bangalore/560075.geojson', 'static/assets/data/pincode-level/bangalore/560076.geojson', 'static/assets/data/pincode-level/bangalore/560077.geojson', 'static/assets/data/pincode-level/bangalore/560078.geojson',
        'static/assets/data/pincode-level/bangalore/560079.geojson', 'static/assets/data/pincode-level/bangalore/560080.geojson', 'static/assets/data/pincode-level/bangalore/560081.geojson', 'static/assets/data/pincode-level/bangalore/560082.geojson',
        'static/assets/data/pincode-level/bangalore/560083.geojson', 'static/assets/data/pincode-level/bangalore/560084.geojson', 'static/assets/data/pincode-level/bangalore/560085.geojson', 'static/assets/data/pincode-level/bangalore/560086.geojson',
        'static/assets/data/pincode-level/bangalore/560087.geojson', 'static/assets/data/pincode-level/bangalore/560088.geojson', 'static/assets/data/pincode-level/bangalore/560089.geojson', 'static/assets/data/pincode-level/bangalore/560090.geojson',
        'static/assets/data/pincode-level/bangalore/560091.geojson', 'static/assets/data/pincode-level/bangalore/560092.geojson', 'static/assets/data/pincode-level/bangalore/560093.geojson', 'static/assets/data/pincode-level/bangalore/560094.geojson',
        'static/assets/data/pincode-level/bangalore/560095.geojson', 'static/assets/data/pincode-level/bangalore/560096.geojson', 'static/assets/data/pincode-level/bangalore/560097.geojson', 'static/assets/data/pincode-level/bangalore/560098.geojson',
        'static/assets/data/pincode-level/bangalore/560099.geojson', 'static/assets/data/pincode-level/bangalore/560100.geojson', 'static/assets/data/pincode-level/bangalore/560102.geojson',
        'static/assets/data/pincode-level/bangalore/560103.geojson', 'static/assets/data/pincode-level/bangalore/560104.geojson', 'static/assets/data/pincode-level/bangalore/560105.geojson', 'static/assets/data/pincode-level/bangalore/560107.geojson',
        'static/assets/data/pincode-level/bangalore/560108.geojson', 'static/assets/data/pincode-level/bangalore/560109.geojson', 'static/assets/data/pincode-level/bangalore/560110.geojson', 'static/assets/data/pincode-level/bangalore/560111.geojson',
        'static/assets/data/pincode-level/bangalore/560112.geojson', 'static/assets/data/pincode-level/bangalore/560113.geojson', 'static/assets/data/pincode-level/bangalore/560114.geojson', 'static/assets/data/pincode-level/bangalore/560115.geojson',
        'static/assets/data/pincode-level/bangalore/560116.geojson', 'static/assets/data/pincode-level/bangalore/560117.geojson', 'static/assets/data/pincode-level/bangalore/560500.geojson', 'static/assets/data/pincode-level/bangalore/562106.geojson',
        'static/assets/data/pincode-level/bangalore/562107.geojson', 'static/assets/data/pincode-level/bangalore/562123.geojson', 'static/assets/data/pincode-level/bangalore/562125.geojson', 'static/assets/data/pincode-level/bangalore/562130.geojson',
        'static/assets/data/pincode-level/bangalore/562149.geojson', 'static/assets/data/pincode-level/bangalore/562157.geojson', 'static/assets/data/pincode-level/bangalore/562162.geojson',];
    } else {
      this.minLatitude = 28.4;
      this.maxLatitude = 28.8;
      this.minLongitude = 77.1;
      this.maxLongitude = 77.4;
      this.geojsonFiles =  ['static/assets/data/pincode-level/delhi/110001.geojson','static/assets/data/pincode-level/delhi/110002.geojson','static/assets/data/pincode-level/delhi/110003.geojson','static/assets/data/pincode-level/delhi/110004.geojson',
        'static/assets/data/pincode-level/delhi/110005.geojson', 'static/assets/data/pincode-level/delhi/110006.geojson','static/assets/data/pincode-level/delhi/110007.geojson','static/assets/data/pincode-level/delhi/110008.geojson',
        'static/assets/data/pincode-level/delhi/110009.geojson', 'static/assets/data/pincode-level/delhi/110010.geojson','static/assets/data/pincode-level/delhi/110011.geojson','static/assets/data/pincode-level/delhi/110012.geojson',
        'static/assets/data/pincode-level/delhi/110013.geojson', 'static/assets/data/pincode-level/delhi/110014.geojson','static/assets/data/pincode-level/delhi/110015.geojson','static/assets/data/pincode-level/delhi/110016.geojson',
        'static/assets/data/pincode-level/delhi/110017.geojson','static/assets/data/pincode-level/delhi/110018.geojson','static/assets/data/pincode-level/delhi/110019.geojson','static/assets/data/pincode-level/delhi/110020.geojson',
        'static/assets/data/pincode-level/delhi/110021.geojson','static/assets/data/pincode-level/delhi/110022.geojson','static/assets/data/pincode-level/delhi/110023.geojson','static/assets/data/pincode-level/delhi/110024.geojson',
        'static/assets/data/pincode-level/delhi/110025.geojson','static/assets/data/pincode-level/delhi/110026.geojson','static/assets/data/pincode-level/delhi/110027.geojson','static/assets/data/pincode-level/delhi/110028.geojson',
        'static/assets/data/pincode-level/delhi/110029.geojson','static/assets/data/pincode-level/delhi/110030.geojson','static/assets/data/pincode-level/delhi/110031.geojson', 'static/assets/data/pincode-level/delhi/110032.geojson',
        'static/assets/data/pincode-level/delhi/110033.geojson','static/assets/data/pincode-level/delhi/110034.geojson','static/assets/data/pincode-level/delhi/110035.geojson','static/assets/data/pincode-level/delhi/110036.geojson',
        'static/assets/data/pincode-level/delhi/110037.geojson','static/assets/data/pincode-level/delhi/110038.geojson','static/assets/data/pincode-level/delhi/110039.geojson','static/assets/data/pincode-level/delhi/110040.geojson',
        'static/assets/data/pincode-level/delhi/110041.geojson','static/assets/data/pincode-level/delhi/110042.geojson','static/assets/data/pincode-level/delhi/110043.geojson','static/assets/data/pincode-level/delhi/110044.geojson',
        'static/assets/data/pincode-level/delhi/110045.geojson','static/assets/data/pincode-level/delhi/110046.geojson','static/assets/data/pincode-level/delhi/110047.geojson','static/assets/data/pincode-level/delhi/110048.geojson',
        'static/assets/data/pincode-level/delhi/110049.geojson','static/assets/data/pincode-level/delhi/110050.geojson','static/assets/data/pincode-level/delhi/110051.geojson',
        'static/assets/data/pincode-level/delhi/110052.geojson','static/assets/data/pincode-level/delhi/110053.geojson','static/assets/data/pincode-level/delhi/110054.geojson','static/assets/data/pincode-level/delhi/110055.geojson',
        'static/assets/data/pincode-level/delhi/110056.geojson', 'static/assets/data/pincode-level/delhi/110057.geojson','static/assets/data/pincode-level/delhi/110058.geojson','static/assets/data/pincode-level/delhi/110059.geojson',
        'static/assets/data/pincode-level/delhi/110060.geojson', 'static/assets/data/pincode-level/delhi/110061.geojson','static/assets/data/pincode-level/delhi/110062.geojson','static/assets/data/pincode-level/delhi/110063.geojson',
        'static/assets/data/pincode-level/delhi/110064.geojson', 'static/assets/data/pincode-level/delhi/110065.geojson','static/assets/data/pincode-level/delhi/110066.geojson','static/assets/data/pincode-level/delhi/110067.geojson',
        'static/assets/data/pincode-level/delhi/110068.geojson','static/assets/data/pincode-level/delhi/110069.geojson','static/assets/data/pincode-level/delhi/110070.geojson','static/assets/data/pincode-level/delhi/110071.geojson',
        'static/assets/data/pincode-level/delhi/110072.geojson','static/assets/data/pincode-level/delhi/110073.geojson','static/assets/data/pincode-level/delhi/110074.geojson','static/assets/data/pincode-level/delhi/110075.geojson',
        'static/assets/data/pincode-level/delhi/110076.geojson','static/assets/data/pincode-level/delhi/110077.geojson','static/assets/data/pincode-level/delhi/110078.geojson',
        'static/assets/data/pincode-level/delhi/110080.geojson','static/assets/data/pincode-level/delhi/110081.geojson','static/assets/data/pincode-level/delhi/110082.geojson', 'static/assets/data/pincode-level/delhi/110083.geojson',
        'static/assets/data/pincode-level/delhi/110084.geojson','static/assets/data/pincode-level/delhi/110085.geojson','static/assets/data/pincode-level/delhi/110086.geojson','static/assets/data/pincode-level/delhi/110087.geojson',
        'static/assets/data/pincode-level/delhi/110088.geojson','static/assets/data/pincode-level/delhi/110089.geojson','static/assets/data/pincode-level/delhi/110090.geojson','static/assets/data/pincode-level/delhi/110091.geojson',
        'static/assets/data/pincode-level/delhi/110092.geojson','static/assets/data/pincode-level/delhi/110093.geojson','static/assets/data/pincode-level/delhi/110094.geojson','static/assets/data/pincode-level/delhi/110095.geojson',
        'static/assets/data/pincode-level/delhi/110096.geojson','static/assets/data/pincode-level/delhi/110097.geojson','static/assets/data/pincode-level/delhi/110098.geojson','static/assets/data/pincode-level/delhi/110099.geojson',
        'static/assets/data/pincode-level/delhi/110100.geojson'];
        
    }
    if (this.map) {
      this.map.off();
      this.map.remove();
    }
    this.initMap();
    this.loadGeoJSONFiles(this.geojsonFiles, (combinedGeoJSON: any) => {
      this.loadCSVData(`static/assets/data/lats-long/${this.city.toLowerCase()}_lats_longs.csv`, (csvData: any) => {
        const filteredData = this.filterCSVData(csvData);
        this.updateMapAndBubbles(filteredData);

        d3.select('#dateFilterDropdown').on('change', () => {
          const selectedMonth = (d3.select('#dateFilterDropdown').node() as HTMLSelectElement).value;
          this.filterDataByDate(filteredData, selectedMonth);
        });
      });
    });
  }

  private initMap(): void {
    this.map = L.map('map').setView(this.city == 'Bangalore' ? [12.9716, 77.5946] : [28.7041, 77.1025], 10);
    L.tileLayer('', { attribution: '' }).addTo(this.map);
  }

  private loadGeoJSONFiles(files: string[], callback: (combinedGeoJSON: any) => void): void {
    this.combinedGeoJSON = { type: 'FeatureCollection', features: [] };
    let loaded = 0;

    files.forEach((file: string) => {
      d3.json(file).then((data: any) => {
        if (data && data.type === 'Feature' && data.geometry && data.geometry.type === 'MultiPolygon') {
          this.combinedGeoJSON.features.push(data);
        } else {
          console.error(`Invalid GeoJSON structure in file: ${file}`);
        }
        loaded++;
        if (loaded === files.length) {
          callback(this.combinedGeoJSON);
        }
      }).catch(error => {
        console.error(`Error loading file ${file}:`, error);
      });
    });
  }

  private loadCSVData(url: string, callback: (data: any) => void): void {
    d3.csv(url).then(callback).catch(error => {
      console.error(`Error loading CSV data:`, error);
    });
  }

  private filterCSVData(data: any[]): any[] {
    return data.filter(d => {
      const lat = +d.latitude_x;
      const lon = +d.longitude_y;
      return lat >= this.minLatitude && lat <= this.maxLatitude && lon >= this.minLongitude && lon <= this.maxLongitude;
    });
  }

  private updateMapAndBubbles(data: any[]): void {
    const totalTransactionsMap: { [key: string]: number } = {};
    data.forEach((d: any) => {
      totalTransactionsMap[d.pick_up_pincode] = +d.total_transactions;
    });

    L.geoJSON(this.combinedGeoJSON, {
      style: feature => {
        const pincode = feature?.properties?.pincode;
        const totalTransactions = totalTransactionsMap[pincode] || 0;

        const maxTransactions = d3.max(data, (d: any) => +d.total_transactions) || 0;

        const colorScale = d3.scaleSequential(d3.interpolateBlues)
          .domain([0, maxTransactions]);

        return {
          color: 'black',
          weight: 0.5,
          opacity: 1,
          fillOpacity: totalTransactions ? totalTransactions / maxTransactions : 0.1,
          fillColor: colorScale(totalTransactions),
        };
      },
      onEachFeature: (feature, layer) => {
        const pincode = feature?.properties?.pincode;
        const totalTransactions = totalTransactionsMap[pincode] || 0;
        layer.bindPopup(`<b>Pincode:</b> ${pincode}<br><b>Total Transactions:</b> ${totalTransactions}`);
      }
    }).addTo(this.map);

    this.plotBubbles(data);
  }

  private filterDataByDate(data: any[], selectedMonth: string): void {
    if (selectedMonth === 'All') {
      this.updateMapAndBubbles(data);
      d3.select('#totalConfirmedOrders').text('Total Confirmed Orders: N/A');
    } else {
      const filteredDataByDate = data.filter(d => {
        const date = new Date(d.latest_order_date);
        const month = date.getMonth() + 1;
        return month === +selectedMonth;
      });

      const totalConfirmedOrders = d3.sum(filteredDataByDate, d => +d.delivered_orders);
      d3.select('#totalConfirmedOrders').text(`Total Confirmed Orders: ${totalConfirmedOrders}`);

      this.updateMapAndBubbles(filteredDataByDate);
    }
  }

  private plotBubbles(data: any[]): void {
    data.forEach(d => {
      const latitudeX = +d.latitude_x;
      const longitudeY = +d.longitude_y;
      const deliveredPercentage = +d.delivered_percentage;

      if (!isNaN(latitudeX) && !isNaN(longitudeY)) {
        const radius = Math.sqrt(deliveredPercentage) * 20;
        const bubbleColor = 'rgba(0, 123, 255, 0.8)';

        L.circle([latitudeX, longitudeY], {
          weight: 2,
          color: bubbleColor,
          fillColor: bubbleColor,
          fillOpacity: 0.7,
          radius: radius
        }).bindPopup(`<b>Pincode:</b> ${d.pick_up_pincode}<br><b>Delivered Percentage:</b> ${deliveredPercentage}%`)
          .addTo(this.map);
      } else {
        console.error(`Invalid LatLng for pick_up_pincode: ${d.pick_up_pincode}`);
      }
    });
  }
}