
/**
 * @param {Object} dump - json dump of the connection
 * @returns {string} - a hash of the connections json dump 
 */
export default function hashDump(dump) {
  const sorted = JSON.stringify(sortObject(dump));
  const hash = CryptoJS.SHA256(sorted).toString(CryptoJS.enc.Hex);
  return hash;
}

// object must be sorted to ensure hashing is consistent 
const sortObject = (obj) => {
  if (typeof obj !== "object" || obj === null) {
    return obj;
  }

  if (Array.isArray(obj)) {
    return obj.map(sortObject);
  }

  const sortedKeys = Object.keys(obj).sort();
  const result = {};
  sortedKeys.forEach((key) => {
    result[key] = sortObject(obj[key]);
  });
  return result;
};