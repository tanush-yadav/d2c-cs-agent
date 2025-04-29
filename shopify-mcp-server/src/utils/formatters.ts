/**
 * Formatters for Shopify data
 */
import { ProductNode, ShopifyOrderGraphql } from '../ShopifyClient/ShopifyClientPort.js';

/**
 * Format a product for display
 * @param product The product to format
 * @returns Formatted product string
 */
export function formatProduct(product: ProductNode): string {
  return `
  Product: ${product.title}
  description: ${product.description}
  handle: ${product.handle}
  variants: ${product.variants.edges
    .map(
      (variant) => `variant.title: ${variant.node.title}
    variant.id: ${variant.node.id}
    variant.price: ${variant.node.price}
    variant.sku: ${variant.node.sku}
    variant.inventoryPolicy: ${variant.node.inventoryPolicy}
    `
    )
    .join(', ')}
  `;
}

/**
 * Format an order for display
 * @param order The order to format
 * @returns Formatted order string
 */
export function formatOrder(order: ShopifyOrderGraphql): string {
  let fulfillmentInfo = 'No fulfillment information';
  if (order.fulfillments && order.fulfillments.length > 0) {
    const fulfillment = order.fulfillments[0];
    fulfillmentInfo = `
  Fulfillment Status: ${fulfillment.status}
  Fulfilled At: ${fulfillment.createdAt}`;
    if (fulfillment.trackingInfo && fulfillment.trackingInfo.length > 0) {
      const tracking = fulfillment.trackingInfo[0];
      fulfillmentInfo += `
  Tracking Number: ${tracking.number}
  Tracking Company: ${tracking.company}
  Tracking URL: ${tracking.url}`;
    }
  }

  // Extract the numeric ID from the full GraphQL ID
  const numericOrderId = order.id.split('/').pop();
  const numericCustomerId = order.customer?.id.split('/').pop();

  return `
  Order name : ${order.name}
  Order ID: ${numericOrderId}
  Created At: ${order.createdAt}
  Status: ${order.displayFinancialStatus || 'N/A'}
  Email: ${order.email || 'N/A'}
  Phone: ${order.phone || 'N/A'}

  Total Price: ${order.totalPriceSet.shopMoney.amount} ${
    order.totalPriceSet.shopMoney.currencyCode
  }

  Customer: ${
    order.customer
      ? `
    ID: ${numericCustomerId}
    Email: ${order.customer.email}`
      : 'No customer information'
  }

  Shipping Address: ${
    order.shippingAddress
      ? `
    Province: ${order.shippingAddress.provinceCode || 'N/A'}
    Country: ${order.shippingAddress.countryCode}`
      : 'No shipping address'
  }

  Details: ${
    order.lineItems.nodes.length > 0
      ? order.lineItems.nodes
          .map(
            (item) => `
    Title: ${item.title}
    Quantity: ${item.quantity}
    Price: ${item.originalTotalSet.shopMoney.amount} ${
              item.originalTotalSet.shopMoney.currencyCode
            }
    Variant: ${
      item.variant
        ? `
      Title: ${item.variant.title}
      SKU: ${item.variant.sku || 'N/A'}
      Price: ${item.variant.price}`
        : 'No variant information'
    }`
          )
          .join('\n')
      : 'No items'
  }

  ${fulfillmentInfo}
  `;
}