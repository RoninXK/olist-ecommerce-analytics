SELECT
    COUNT(DISTINCT order_id)
        AS pedidos,

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

WHERE order_status = 'delivered';