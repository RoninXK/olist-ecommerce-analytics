SELECT
    customer_state AS estado,

    COUNT(DISTINCT order_id)
        AS pedidos,

    COUNT(DISTINCT customer_unique_id)
        AS clientes,

    ROUND(
        SUM(payment_total),
        2
    ) AS faturamento,

    ROUND(
        SUM(payment_total)
        /
        COUNT(DISTINCT order_id),
        2
    ) AS ticket_medio

FROM orders

WHERE order_status = 'delivered'

GROUP BY customer_state

ORDER BY faturamento DESC;