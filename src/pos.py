#!/usr/bin/env python3
"""Simple CLI POS program."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


CURRENCY_PLACES = Decimal("0.01")


def to_decimal(value: str) -> Decimal:
    try:
        return Decimal(value).quantize(CURRENCY_PLACES, rounding=ROUND_HALF_UP)
    except Exception as exc:  # noqa: BLE001 - provide friendly error
        raise ValueError("금액은 숫자로 입력해주세요.") from exc


@dataclass
class Item:
    name: str
    price: Decimal


@dataclass
class CartLine:
    item: Item
    quantity: int

    @property
    def subtotal(self) -> Decimal:
        return (self.item.price * Decimal(self.quantity)).quantize(
            CURRENCY_PLACES, rounding=ROUND_HALF_UP
        )


@dataclass
class Cart:
    lines: List[CartLine] = field(default_factory=list)

    def add_item(self, item: Item, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("수량은 1개 이상이어야 합니다.")
        for line in self.lines:
            if line.item.name == item.name:
                line.quantity += quantity
                return
        self.lines.append(CartLine(item=item, quantity=quantity))

    def total(self) -> Decimal:
        return sum((line.subtotal for line in self.lines), Decimal("0.00")).quantize(
            CURRENCY_PLACES, rounding=ROUND_HALF_UP
        )


class PosApp:
    def __init__(self) -> None:
        self.inventory: Dict[str, Item] = {}
        self.cart = Cart()

    def register_item(self) -> None:
        name = input("상품명: ").strip()
        if not name:
            print("상품명을 입력해주세요.")
            return
        price_input = input("가격: ").strip()
        try:
            price = to_decimal(price_input)
        except ValueError as error:
            print(error)
            return
        self.inventory[name] = Item(name=name, price=price)
        print(f"등록 완료: {name} - {price}원")

    def list_inventory(self) -> None:
        if not self.inventory:
            print("등록된 상품이 없습니다.")
            return
        print("=== 상품 목록 ===")
        for item in self.inventory.values():
            print(f"- {item.name}: {item.price}원")

    def add_to_cart(self) -> None:
        if not self.inventory:
            print("먼저 상품을 등록해주세요.")
            return
        name = input("추가할 상품명: ").strip()
        if name not in self.inventory:
            print("해당 상품이 없습니다.")
            return
        qty_input = input("수량: ").strip()
        try:
            quantity = int(qty_input)
        except ValueError:
            print("수량은 숫자로 입력해주세요.")
            return
        try:
            self.cart.add_item(self.inventory[name], quantity)
        except ValueError as error:
            print(error)
            return
        print(f"장바구니에 추가: {name} x {quantity}")

    def checkout(self) -> None:
        if not self.cart.lines:
            print("장바구니가 비어있습니다.")
            return
        print("=== 결제 내역 ===")
        for line in self.cart.lines:
            print(
                f"- {line.item.name} ({line.quantity}개): {line.subtotal}원"
            )
        total = self.cart.total()
        print(f"총합: {total}원")
        discount_input = input("할인 금액(없으면 0): ").strip() or "0"
        try:
            discount = to_decimal(discount_input)
        except ValueError as error:
            print(error)
            return
        final_total = (total - discount).quantize(
            CURRENCY_PLACES, rounding=ROUND_HALF_UP
        )
        if final_total < 0:
            print("할인 금액이 총합보다 큽니다.")
            return
        print(f"결제 금액: {final_total}원")
        paid_input = input("받은 금액: ").strip()
        try:
            paid = to_decimal(paid_input)
        except ValueError as error:
            print(error)
            return
        if paid < final_total:
            print("받은 금액이 부족합니다.")
            return
        change = (paid - final_total).quantize(
            CURRENCY_PLACES, rounding=ROUND_HALF_UP
        )
        print(f"거스름돈: {change}원")
        self.cart = Cart()

    def run(self) -> None:
        menu = (
            "\n=== POS 메뉴 ===\n"
            "1) 상품 등록\n"
            "2) 상품 목록\n"
            "3) 장바구니 추가\n"
            "4) 결제\n"
            "5) 종료\n"
        )
        actions = {
            "1": self.register_item,
            "2": self.list_inventory,
            "3": self.add_to_cart,
            "4": self.checkout,
        }
        while True:
            print(menu)
            choice = input("선택: ").strip()
            if choice == "5":
                print("프로그램을 종료합니다.")
                break
            action = actions.get(choice)
            if not action:
                print("올바른 메뉴를 선택해주세요.")
                continue
            action()


if __name__ == "__main__":
    PosApp().run()
