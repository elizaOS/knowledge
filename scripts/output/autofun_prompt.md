# 10 auto.fun tweet ideas:

1. just shipped scopable knowledge in auto.fun v2. now your agents can access different knowledge bases based on context without leaking info where it shouldn't go. privacy + performance in one commit.

2. fixed discord plugin typing indicators so your agents look alive while thinking. no more awkward silence in the chat, just natural convos that feel less botty and more human.

3. cli command update just dropped for elizaos v2. cleaner syntax, better error messages, and actually helpful instructions when you run create. dev ux matters too anon.

4. postgres docker container was failing health checks because we forgot to escape a single character. classic dev moment. fixed now though so your deployments won't randomly explode.

5. anthropic plugin now validates your api key before attempting calls instead of failing silently. small change but saves you from debugging hell. you're welcome.

6. auto.fun agents now log which model/plugin they're using during inference. finally some transparency into what's happening under the hood without having to dig through logs.

7. esm type declarations in core were broken, causing ts errors in downstream projects. fixed now so you can import from @elizaos/core without typescript screaming at you.

8. implemented proper error handling for "no space left on disk" so instead of cryptic crashes you'll get actual human readable messages. infrastructure is code too fam.

9. monorepo dev experience massively improved - core and plugin-bootstrap now auto-rebuild when you run dev command. no more manual rebuilds every time you change something.

10. fixed agent deletion that was leaving orphaned processes. memory leaks are cringe, clean exits are based. your server thanks us.

# Twitter Thread:

1/ just dropped a major auto.fun update with scopable knowledge for your agents. now they can access different knowledge bases based on context without leaking info where it shouldn't. privacy + performance in one commit. dev experience matters.

2/ fixed multiple pain points for builders: discord typing indicators, anthropic api validation, postgres container health checks, and esm type declarations in core. small fixes that make big differences when you're shipping code at 3am.

3/ for the terminal-dwellers: cli command updates with better instructions, error handling for disk space issues, and auto-rebuilds in monorepo context. your dev environment should just work - now it does. grab the latest with npx elizaos update-cli.
