CREATE OR REPLACE VIEW v_scene_relation AS
WITH RECURSIVE relation AS (
    -- ① 基础层：每个节点先作为“自己的祖先”
    SELECT
        id  AS ancestor_id,
        id  AS descendant_id,
        0   AS depth
    FROM pro_scene
    WHERE is_delete = 0

    UNION ALL

    -- ② 递归层：在已有(祖先→当前节点)的基础上，往下找“子节点”
    SELECT
        r.ancestor_id,
        c.id        AS descendant_id,
        r.depth + 1 AS depth
    FROM pro_scene c
    JOIN relation r
        ON c.parent_id = r.descendant_id
    WHERE c.is_delete = 0
)
-- ③ 最终层：只要真正的祖先→后代（去掉自己指向自己）
SELECT
    CONCAT(ancestor_id, '_', descendant_id) AS id,   -- ✅ 唯一 id：祖先_子孙
    ancestor_id,
    descendant_id,
    depth
FROM relation
WHERE depth > 0;
