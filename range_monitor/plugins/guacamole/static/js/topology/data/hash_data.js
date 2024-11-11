

/**
 * @param {Object} dump - a Node JSON representation 
 * @returns {string} - a hash of json 
 */
export default function hashDump(dump) {
  const sorted = JSON.stringify(sortObject(dump));
  const hash = CryptoJS.SHA256(sorted).toString(CryptoJS.enc.Hex);
  return hash;
}

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