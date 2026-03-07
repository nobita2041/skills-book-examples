"""E2E tests for Task Manager app: add, complete, and delete tasks."""

import re
from playwright.sync_api import sync_playwright, expect

APP_URL = "http://localhost:5173"


def test_task_operations():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(APP_URL)
        page.wait_for_load_state("networkidle")

        # --- Clear localStorage to start fresh ---
        page.evaluate("localStorage.clear()")
        page.reload()
        page.wait_for_load_state("networkidle")

        # Verify empty state
        expect(page.get_by_text("タスクがありません")).to_be_visible()
        print("[PASS] Empty state displayed correctly")

        # === Test 1: Add tasks ===
        input_field = page.get_by_placeholder("新しいタスクを入力...")
        submit_button = page.locator('button[type="submit"]')

        # Add first task
        input_field.fill("買い物に行く")
        submit_button.click()
        expect(page.get_by_text("買い物に行く")).to_be_visible()
        expect(page.get_by_text(re.compile(r"^未完了 \(1\)$"))).to_be_visible()
        print("[PASS] Task 1 added: 買い物に行く")

        # Add second task
        input_field.fill("レポートを書く")
        submit_button.click()
        expect(page.get_by_text("レポートを書く")).to_be_visible()
        expect(page.get_by_text(re.compile(r"^未完了 \(2\)$"))).to_be_visible()
        print("[PASS] Task 2 added: レポートを書く")

        # Add third task
        input_field.fill("メールを返信する")
        submit_button.click()
        expect(page.get_by_text("メールを返信する")).to_be_visible()
        expect(page.get_by_text(re.compile(r"^未完了 \(3\)$"))).to_be_visible()
        print("[PASS] Task 3 added: メールを返信する")

        # Verify empty input doesn't add task
        submit_button_disabled = page.locator('button[type="submit"][disabled]')
        expect(submit_button_disabled).to_be_visible()
        print("[PASS] Submit button disabled when input is empty")

        # Take screenshot after adding tasks
        page.screenshot(path="/tmp/e2e_after_add.png", full_page=True)

        # === Test 2: Complete a task ===
        # Click checkbox for "買い物に行く"
        task1_checkbox = page.locator("label", has_text="買い物に行く").locator("..").locator('button[role="checkbox"]')
        task1_checkbox.click()

        expect(page.get_by_text(re.compile(r"^未完了 \(2\)$"))).to_be_visible()
        expect(page.get_by_text(re.compile(r"^完了 \(1\)$"))).to_be_visible()
        print("[PASS] Task completed: 買い物に行く moved to completed section")

        # Complete another task
        task2_checkbox = page.locator("label", has_text="レポートを書く").locator("..").locator('button[role="checkbox"]')
        task2_checkbox.click()

        expect(page.get_by_text(re.compile(r"^未完了 \(1\)$"))).to_be_visible()
        expect(page.get_by_text(re.compile(r"^完了 \(2\)$"))).to_be_visible()
        print("[PASS] Task completed: レポートを書く moved to completed section")

        # Verify completed task has line-through style
        completed_label = page.locator("label.line-through", has_text="買い物に行く")
        expect(completed_label).to_be_visible()
        print("[PASS] Completed task has line-through style")

        # Take screenshot after completing tasks
        page.screenshot(path="/tmp/e2e_after_complete.png", full_page=True)

        # === Test 3: Uncomplete a task (toggle back) ===
        task1_checkbox_again = page.locator("label", has_text="買い物に行く").locator("..").locator('button[role="checkbox"]')
        task1_checkbox_again.click()

        expect(page.get_by_text(re.compile(r"^未完了 \(2\)$"))).to_be_visible()
        expect(page.get_by_text(re.compile(r"^完了 \(1\)$"))).to_be_visible()
        print("[PASS] Task uncompleted: 買い物に行く moved back to pending")

        # === Test 4: Delete a task ===
        # Hover to reveal delete button, then click it
        task_row = page.locator("div.group", has_text="メールを返信する")
        task_row.hover()
        delete_btn = task_row.get_by_label("Delete task")
        delete_btn.click()

        expect(page.get_by_text("メールを返信する")).not_to_be_visible()
        expect(page.get_by_text(re.compile(r"^未完了 \(1\)$"))).to_be_visible()
        print("[PASS] Task deleted: メールを返信する")

        # Delete a completed task
        completed_row = page.locator("div.group", has_text="レポートを書く")
        completed_row.hover()
        completed_row.get_by_label("Delete task").click()

        expect(page.get_by_text("レポートを書く")).not_to_be_visible()
        # Only "完了" section should disappear since no completed tasks remain
        expect(page.get_by_text(re.compile(r"^完了 \(\d+\)$"))).not_to_be_visible()
        print("[PASS] Completed task deleted: レポートを書く")

        # Take screenshot after deletions
        page.screenshot(path="/tmp/e2e_after_delete.png", full_page=True)

        # === Test 5: Delete last remaining task -> empty state ===
        last_row = page.locator("div.group", has_text="買い物に行く")
        last_row.hover()
        last_row.get_by_label("Delete task").click()

        expect(page.get_by_text("タスクがありません")).to_be_visible()
        print("[PASS] All tasks deleted, empty state restored")

        # Final screenshot
        page.screenshot(path="/tmp/e2e_final.png", full_page=True)

        print("\n=== All E2E tests passed! ===")
        browser.close()


if __name__ == "__main__":
    test_task_operations()
