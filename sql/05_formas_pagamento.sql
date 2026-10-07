SELECT
    payment_type AS forma_pagamento,

    COUNT(DISTINCT order_id)
        AS pedidos,

    COUNT(*)
        AS transacoes,

    ROUND(
        SUM(payment_value),
        2
    ) AS valor_total,

    ROUND(
        AVG(payment_installments),
        2
    ) AS parcelas_media

FROM payments

GROUP BY payment_type

ORDER BY valor_total DESC;