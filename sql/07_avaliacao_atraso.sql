SELECT

    CASE

        WHEN delivery_difference_days > 0
        THEN 'Atrasado'

        ELSE 'No prazo'

    END AS situacao_entrega,

    COUNT(DISTINCT order_id)
        AS pedidos,

    ROUND(
        AVG(review_score),
        2
    ) AS nota_media

FROM orders

WHERE
    order_status = 'delivered'

    AND review_score IS NOT NULL

    AND delivery_difference_days
        IS NOT NULL

GROUP BY situacao_entrega;