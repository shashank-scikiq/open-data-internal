function formatNumber(num)
{
   var num_parts = num.toString().split(".");
   num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
   return num_parts.join(".");
}
export function updateTopCardMetrics(id, data, changeid, datachange) {
   const element = document.getElementById(id);
   const changeElement = document.getElementById(changeid);

   const numericData = Number(data);
   if (!isNaN(numericData)) {
       element.innerText = `${formatNumber(numericData)}`;
   } else {
       element.innerText = data;
   }

   const numericDataChange = Number(datachange);
   if (!isNaN(numericDataChange)) {
       if (numericDataChange >= 0) {
           changeElement.innerText = `${formatNumber(numericDataChange)}`;
       } else {
           changeElement.innerText = `${formatNumber(numericDataChange)}`;
       }
   } else {
       changeElement.innerText = datachange;
   }
}

