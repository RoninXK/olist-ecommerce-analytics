SELECT
    ROUND(SUM(payment_total), 2)
        AS faturamento_total,

    COUNT(DISTINCT order_id)
        AS total_pedidos

FROM orders

WHERE order_status = 'delivered';