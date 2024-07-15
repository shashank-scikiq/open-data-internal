// eventHandlers.js
import * as FetchData from './fetchData';
import * as ProcessData from './processData';
import * as UpdateUI from './updateUI';

export async function handleStateChange(event) {
    const selectedStateCode = event.target.value;

    try {
        const stateData = await FetchData.fetchSpecificStateData(selectedStateCode);

        const processedData = ProcessData.processStateData(stateData);

        UpdateUI.updateStateUI(processedData);
    } catch (error) {
        console.error('Error handling state change:', error);
    }
}
