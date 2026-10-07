SELECT
    product_category AS categoria,

    COUNT(*) AS itens_vendidos,

    COUNT(DISTINCT order_id)
        AS pedidos,

    ROUND(
        SUM(price),
        2
    ) AS faturamento_produtos,

    ROUND(
        AVG(price),
        2
    ) AS preco_medio,

    ROUND(
        SUM(freight_value),
        2
    ) AS frete_total

FROM order_items

WHERE order_status = 'delivered'

GROUP BY product_category

ORDER BY faturamento_produtos DESC

LIMIT 20;