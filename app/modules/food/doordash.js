const fetch = require('node-fetch');
const settings = require('../../utils/settings');

async function orderBreakfast(itemId) {
  const apiKey = settings.get('doordashApiKey');
  const addressId = settings.get('defaultAddressId');

  const response = await fetch('https://api.doordash.com/v1/orders', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      store_id: 'YOUR_FAVORITE_STORE_ID',
      items: [{ item_id: itemId, quantity: 1 }],
      address_id: addressId
    })
  });

  return response.json();
}

module.exports = { orderBreakfast };
