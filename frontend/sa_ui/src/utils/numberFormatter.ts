// src/utils/numberFormatter.ts

/**
 * 格式化大数字为易读形式
 * 例如：12345678 -> 1234.57万
 * @param num 要格式化的数字
 * @param digits 保留小数位数，默认2位
 * @returns 格式化后的字符串
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
   * 格式化百分比
   * @param value 原始值（如0.1256）
   * @param digits 保留小数位数，默认2位
   * @returns 格式化后的百分比（如12.56%）
   */
  export function formatPercent(value: number, digits: number = 2): string {
    if (value === null || value === undefined) return '-';
    return (value * 100).toFixed(digits) + '%';
  }
  
  /**
   * 格式化金额，添加千位分隔符
   * @param value 金额数值
   * @param digits 保留小数位数，默认2位
   * @returns 格式化后的金额字符串
   */
  export function formatCurrency(value: number, digits: number = 2): string {
    if (value === null || value === undefined) return '-';
    
    // 添加千位分隔符
    return value.toLocaleString('zh-CN', {
      minimumFractionDigits: digits,
      maximumFractionDigits: digits
    });
  }
  
  /**
   * 转换成万/亿单位，超过100万的数字才转换
   * @param value 数值
   * @param digits 保留小数位数
   * @returns 转换后的字符串
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