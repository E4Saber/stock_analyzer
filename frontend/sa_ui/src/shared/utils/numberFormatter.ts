// src/utils/numberFormatter.ts

/**
 * Format large numbers for readability
 * Example: 12345678 -> 1234.57万
 * @param num Number to format
 * @param digits Decimal digits to keep, defaults to 2
 * @returns Formatted string
 */
export function formatLargeNumber(num: number, digits: number = 2): string {
  if (num === null || num === undefined) return '-';
  
  if (num >= 1000000000000) {
    return (num / 1000000000000).toFixed(digits) + '万亿';
  } else if (num >= 100000000) {
    return (num / 100000000).toFixed(digits) + '亿';
  } else if (num >= 10000) {
    return (num / 10000).toFixed(digits) + '万';
  } else {
    return num.toFixed(0);
  }
}

/**
 * Format percentage
 * @param value Raw value (like 0.1256)
 * @param digits Decimal digits to keep, defaults to 2
 * @returns Formatted percentage (like 12.56%)
 */
export function formatPercent(value: number, digits: number = 2): string {
  if (value === null || value === undefined) return '-';
  return (value * 100).toFixed(digits) + '%';
}

/**
 * Format currency with thousands separator
 * @param value Amount
 * @param digits Decimal digits to keep, defaults to 2
 * @returns Formatted currency string
 */
export function formatCurrency(value: number, digits: number = 2): string {
  if (value === null || value === undefined) return '-';
  
  // Add thousands separator
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  });
}

/**
 * Convert to million/billion units, only for numbers over 1,000,000
 * @param value Number
 * @param digits Decimal digits
 * @returns Formatted string
 */
export function formatCompactNumber(value: number, digits: number = 2): string {
  if (value === null || value === undefined) return '-';
  
  if (Math.abs(value) >= 100000000) {
    return (value / 100000000).toFixed(digits) + '亿';
  } else if (Math.abs(value) >= 10000) {
    return (value / 10000).toFixed(digits) + '万';
  } else {
    return value.toFixed(digits);
  }
}