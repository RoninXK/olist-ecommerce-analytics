SELECT
    customer_state AS estado,

    COUNT(DISTINCT order_id)
        AS pedidos_entregues,

    ROUND(
        AVG(delivery_days),
        2
    ) AS tempo_medio_entrega,

    SUM(
        CASE
            WHEN delivery_difference_days > 0
            THEN 1
            ELSE 0
        END
    ) AS pedidos_atrasados,

    ROUND(
        100.0
        *
        SUM(
            CASE
                WHEN delivery_difference_days > 0
                THEN 1
                ELSE 0
            END
        )
        /
        COUNT(*),
        2
    ) AS percentual_atrasados

FROM orders

WHERE
    order_status = 'delivered'

    AND delivery_difference_days
        IS NOT NULL

GROUP BY customer_state

ORDER BY percentual_atrasados DESC;