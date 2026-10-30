import { categoryInfo, type Category } from '../data'

export default function CategoryTag({ category }: { category: Category }) {
  const { label, color, icon: Icon } = categoryInfo(category)
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wider"
      style={{ color, backgroundColor: `${color}18` }}
    >
      <Icon className="size-3.5" />
      {label}
    </span>
  )
}
